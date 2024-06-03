import datetime
import logging

from api.const import TokenType
from flask import current_app, request
from web3 import Web3

from .captcha import captcha_verify
from .csrf import CSRF
from .database import AccessKeyConfig, BlockedUsers, Token, Transaction
from .rate_limit import Strategy

logging.basicConfig(level=logging.INFO)


class AskEndpointValidator:
    errors = []
    http_return_code = None

    messages = {
        'UNSUPPORTED_CHAIN': 'chainId: %s is not supported. Supported chainId: %s',
        'INVALID_RECIPIENT': 'recipient: A valid recipient address must be specified',
        'INVALID_RECIPIENT_ITSELF': 'recipient: address cant\'t be the Faucet address itself',
        'BLOCKED_RECIPIENT': 'Recipient address is blocked',
        'REQUIRED_AMOUNT': 'amount: is required',
        'AMOUNT_ZERO': 'amount: must be greater than 0',
        'INVALID_TOKEN_ADDRESS': 'tokenAddress: A valid token address must be specified',
        'RATE_LIMIT_EXCEEDED': 'recipient: you have exceeded the limit for today. Try again in %d hours'
    }

    def __init__(self, request_data, request_headers, validate_captcha, validate_csrf, access_key=None, *args, **kwargs):
        self.request_data = request_data
        self.request_headers = request_headers
        self.validate_captcha = validate_captcha
        self.validate_csrf = validate_csrf
        self.access_key = access_key
        self.ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        self.errors = []
        self.csrf = CSRF.instance

    def validate(self):
        if self.validate_csrf:
            self.csrf_validation()
            if len(self.errors) > 0:
                return False

        self.blocked_user_validation()
        if len(self.errors) > 0:
            return False

        self.data_validation()
        if len(self.errors) > 0:
            return False

        self.token_validation()
        if len(self.errors) > 0:
            return False

        if self.validate_captcha:
            self.captcha_validation()
            if len(self.errors) > 0:
                return False

            self.web_request_amount_validation()
            if len(self.errors) > 0:
                return False

            self.web_request_limit_validation()
            if len(self.errors) > 0:
                return False

        if self.access_key:
            self.access_key_validation()
            if len(self.errors) > 0:
                return False
        return True

    def csrf_validation(self):
        token = self.request_headers.get('X-CSRFToken', None)
        if not token:
            self.errors.append('Bad request')
            self.http_return_code = 400

        request_id = self.request_data.get('requestId', None)
        if not request_id:
            self.errors.append('Bad request')
            self.http_return_code = 400

        timestamp = self.request_data.get('timestamp', None)
        if not timestamp:
            self.errors.append('Bad request')
            self.http_return_code = 400

        csrf_valid = self.csrf.validate_token(request_id, token, timestamp)
        if not csrf_valid:
            self.errors.append('Bad request')
            self.http_return_code = 400

    def blocked_user_validation(self):
        recipient = self.request_data.get('recipient', None)
        # Run validation on blocked users only if `recipient` is available.
        # Let next validation steps do the rest.
        if recipient:
            # check if recipient in blocked_users, return 403
            user = BlockedUsers.get_by_address(recipient)
            if user:
                self.errors.append(self.messages['BLOCKED_RECIPIENT'])
                self.http_return_code = 403

    def data_validation(self):
        if self.request_data.get('chainId') != current_app.config['FAUCET_CHAIN_ID']:
            self.errors.append(self.messages['UNSUPPORTED_CHAIN'] % (
                self.request_data.get('chainId'),
                current_app.config['FAUCET_CHAIN_ID']))

        recipient = self.request_data.get('recipient', None)
        if not Web3.is_address(recipient):
            self.errors.append(self.messages['INVALID_RECIPIENT'])

        if not recipient or recipient.lower() == current_app.config['FAUCET_ADDRESS']:
            self.errors.append(self.messages['INVALID_RECIPIENT_ITSELF'])

        amount = self.request_data.get('amount', None)
        if not amount:
            self.errors.append(self.messages['REQUIRED_AMOUNT'])
        if amount and float(amount) <= 0:
            self.errors.append(self.messages['AMOUNT_ZERO'])

        token_address = self.request_data.get('tokenAddress', None)
        if not Web3.is_address(token_address):
            self.errors.append(self.messages['INVALID_TOKEN_ADDRESS'])

        if len(self.errors) > 0:
            self.http_return_code = 400
        else:
            self.token_address = Web3.to_checksum_address(token_address)
            self.amount = float(amount)
            self.chain_id = self.request_data.get('chainId')
            self.recipient = recipient

    def captcha_validation(self):
        error_key = 'captcha'
        # check hcatpcha
        catpcha_verified = captcha_verify(
            self.request_data.get('captcha'),
            current_app.config['CAPTCHA_VERIFY_ENDPOINT'],
            current_app.config['CAPTCHA_SECRET_KEY'],
            self.ip_address,
            current_app.config['CAPTCHA_SITE_KEY']
        )

        if not catpcha_verified:
            self.errors.append('%s: validation failed' % error_key)

        if len(self.errors) > 0:
            self.http_return_code = 400

    def token_validation(self):
        self.token = Token.get_by_address_and_chain_id(self.token_address,
                                                       self.chain_id)
        error_key = 'tokenAddress'

        if not self.token:
            self.errors.append('%s: token not available for chainId %s' % (
                error_key,
                self.chain_id))
        if self.token and self.token.enabled is False:
            self.errors.append('%s: %s is not enabled' % (error_key,
                                                          self.token_address))

        if len(self.errors) > 0:
            self.http_return_code = 400

    def web_request_amount_validation(self):
        if self.amount > self.token.max_amount_day:
            self.errors.append('amount: must be less or equals to %s' % self.token.max_amount_day)
            # except ValueError as e:
            #     message = "".join([arg for arg in e.args])
            #     validation_errors.append(message)

        if len(self.errors) > 0:
            self.http_return_code = 400

    def web_request_limit_validation(self):
        if current_app.config['FAUCET_RATE_LIMIT_STRATEGY'].strategy == Strategy.address.value:
            # Check last claim by recipient
            transaction = Transaction.last_by_recipient(self.recipient)
        elif current_app.config['FAUCET_RATE_LIMIT_STRATEGY'].strategy == Strategy.ip.value:
            # Check last claim by IP
            transaction = Transaction.last_by_ip(self.ip_address)
        elif current_app.config['FAUCET_RATE_LIMIT_STRATEGY'].strategy == Strategy.ip_and_address.value:
            transaction = Transaction.last_by_ip_and_recipient(self.ip_address,
                                                               self.recipient)
        elif current_app.config['FAUCET_RATE_LIMIT_STRATEGY'].strategy == Strategy.ip_or_address.value:
            transaction = Transaction.last_by_ip_or_recipient(self.ip_address,
                                                              self.recipient)
        else:
            raise NotImplementedError

        # Check if the recipient can claim funds, they must not have claimed any tokens
        # in the period of time defined by FAUCET_RATE_LIMIT_TIME_LIMIT_SECONDS
        if transaction:
            time_diff_seconds = (datetime.datetime.utcnow() - transaction.created).total_seconds()
            if time_diff_seconds < current_app.config['FAUCET_RATE_LIMIT_TIME_LIMIT_SECONDS']:
                time_limit_hours = current_app.config['FAUCET_RATE_LIMIT_TIME_LIMIT_SECONDS'] / (24*60)
                time_diff_hours = time_limit_hours-(time_diff_seconds/(24*60))
                self.errors.append(
                    self.messages['RATE_LIMIT_EXCEEDED'] % (
                        round(time_diff_hours, 2)
                    )
                )

        if len(self.errors) > 0:
            self.http_return_code = 429

    def access_key_validation(self):
        # check available amount for the given access key and token
        access_key_config = AccessKeyConfig.get_by_key_id_and_chain_id(
            self.access_key.access_key_id, self.token.chain_id)

        timerange = datetime.datetime.now() - datetime.timedelta(
            seconds=current_app.config['FAUCET_RATE_LIMIT_TIME_LIMIT_SECONDS'])

        # get amount from the last X hours
        past_amount = Transaction.get_amount_sum_by_access_key_and_token(
            self.access_key.access_key_id,
            self.token.address,
            custom_timerange=timerange)
        total_amount = (past_amount or 0) + self.amount

        if self.token.type == TokenType.native.value:
            if total_amount and total_amount >= access_key_config.native_max_amount_day:
                self.errors.append("requested amount exceeds the limit for today")
        elif self.token.type == TokenType.erc20.value:
            if total_amount and total_amount >= access_key_config.erc20_max_amount_day:
                self.errors.append("requested amount exceeds the limit for today")
        else:
            raise Exception('Unkown token type %s' % self.token.type)

        if len(self.errors) > 0:
            self.http_return_code = 429
