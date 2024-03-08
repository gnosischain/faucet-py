import datetime

from flask import current_app, jsonify, request
from web3 import Web3

from api.const import TokenType

from .captcha import captcha_verify
from .database import AccessKeyConfig, Token, Transaction
from .rate_limit import Strategy


class Validator:
    errors = []
    http_return_code = None

    def __init__(self, request_data, validate_captcha, access_key=None):
        self.request_data = request_data
        self.validate_captcha = validate_captcha
        self.access_key = access_key
        self.ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)

    def validate(self):
        self.data_validation()
        if len(self.errors) > 0:
            return jsonify(errors=self.errors), self.http_return_code

        if self.validate_captcha:
            self.captcha_validation()
            if len(self.errors) > 0:
                return jsonify(errors=self.errors), self.http_return_code

        self.token_validation()
        if len(self.errors) > 0:
            return jsonify(errors=self.errors), self.http_return_code

        if self.validate_captcha:
            self.web_request_validation()
            if len(self.errors) > 0:
                return jsonify(errors=self.errors), self.http_return_code

        if self.access_key:
            self.access_key_validation()
            if len(self.errors) > 0:
                return jsonify(errors=self.errors), self.http_return_code

    def data_validation(self):
        if self.request_data.get('chainId') != current_app.config['FAUCET_CHAIN_ID']:
            self.errors.append('chainId: %s is not supported. Supported chainId: %s' % (
                self.request_data.get('chainId'),
                current_app.config['FAUCET_CHAIN_ID']))

        recipient = self.request_data.get('recipient', None)
        if not Web3.is_address(recipient):
            self.errors.append('recipient: A valid recipient address must be specified')

        if not recipient or recipient.lower() == current_app.config['FAUCET_ADDRESS']:
            self.errors.append('recipient: address cant\'t be the Faucet address itself')

        amount = self.request_data.get('amount', None)
        if not amount:
            self.errors.append('amount: is required')
        if amount and float(amount) <= 0:
            self.errors.append('amount: must be greater than 0')

        token_address = self.request_data.get('tokenAddress', None)
        if not Web3.is_address(token_address):
            self.errors.append('tokenAddress: A valid token address must be specified')

        if len(self.errors) > 0:
            self.http_return_code = 400
        else:
            self.token_address = token_address
            self.amount = float(amount)
            self.chain_id = self.request_data.get('chainId')
            self.recipient = recipient

    def captcha_validation(self):
        error_key = 'captcha'
        # check hcatpcha
        catpcha_verified = captcha_verify(
            self.request_data.get('captcha'),
            current_app.config['CAPTCHA_VERIFY_ENDPOINT'], current_app.config['CAPTCHA_SECRET_KEY']
        )

        if not catpcha_verified:
            self.errors.append('%s: validation failed' % error_key)

        if len(self.errors) > 0:
            self.http_return_code = 400

    def token_validation(self):
        self.token = Token.get_by_address_and_chain_id(self.token_address,
                                                       self.request_data.get('chainId'))
        error_key = 'tokenAddress'

        if not self.token:
            self.errors.append('%s: token not available for chainId %s' % (
                error_key,
                self.request_data.get('chainId')))
        if self.token and self.token.enabled is False:
            self.errors.append('%s: %s is not enabled' % (error_key,
                                                          self.token_address))

        if len(self.errors) > 0:
            self.http_return_code = 400

    def web_request_validation(self):
        if self.amount > self.token.max_amount_day:
            self.errors.append('amount: must be less or equals to %s' % self.token.max_amount_day)
            # except ValueError as e:
            #     message = "".join([arg for arg in e.args])
            #     validation_errors.append(message)

        if current_app.config['FAUCET_RATE_LIMIT_STRATEGY'].strategy == Strategy.address.value:
            # Check last claim by recipient
            transaction = Transaction.last_by_recipient(self.recipient)
        elif current_app.config['FAUCET_RATE_LIMIT_STRATEGY'].strategy == Strategy.ip.value:
            # Check last claim by IP
            transaction = Transaction.last_by_ip(self.ip_address)
        elif current_app.config['FAUCET_RATE_LIMIT_STRATEGY'].strategy == Strategy.ip_and_address.value:
            transaction = Transaction.last_by_ip_and_recipient(self.ip_address, self.recipient)
        elif current_app.config['FAUCET_RATE_LIMIT_STRATEGY'].strategy == Strategy.ip_or_address.value:
            transaction = Transaction.last_by_ip_or_recipient(self.ip_address, self.recipient)
        else:
            raise NotImplementedError

        # Check if the recipient can claim funds, they must not have claimed any tokens 
        # in the period of time defined by FAUCET_RATE_LIMIT_TIME_LIMIT_SECONDS
        if transaction:
            time_diff_seconds = (datetime.datetime.utcnow() - transaction.created).total_seconds()
            if time_diff_seconds < current_app.config['FAUCET_RATE_LIMIT_TIME_LIMIT_SECONDS']:
                time_diff_hours = 24-(time_diff_seconds/(24*60))
                self.errors.append('recipient: you have exceeded the limit for today. Try again in %d hours' % time_diff_hours)
                self.http_return_code = 429

    def access_key_validation(self):
        # check available amount for the given access key and token
        access_key_config = AccessKeyConfig.get_by_key_id_and_chain_id(
            self.access_key.access_key_id, self.token.chain_id)

        timerange = datetime.datetime.now() - datetime.timedelta(
            seconds=current_app.config['FAUCET_RATE_LIMIT_TIME_LIMIT_SECONDS'])

        # get amount from the last X hours
        amount = Transaction.get_amount_sum_by_access_key_and_token(
            self.access_key.access_key_id,
            self.token.address,
            custom_timerange=timerange)

        if self.token.type == TokenType.native.value:
            if amount and amount >= access_key_config.native_max_amount_day:
                self.errors.append("you have exceeded the limit for today")
        elif self.token.type == TokenType.erc20.value:
            if amount and amount >= access_key_config.erc20_max_amount_day:
                self.errors.append("you have exceeded the limit for today")
        else:
            raise Exception('Unkown token type %s' % self.token.type)

        if len(self.errors) > 0:
            self.http_return_code = 429
