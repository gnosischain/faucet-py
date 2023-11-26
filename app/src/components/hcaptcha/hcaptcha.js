import { useEffect, useState, Fragment } from "react";
import HCaptcha from "@hcaptcha/react-hcaptcha";

import { Container } from "@mui/system";
import {
  Button,
  Grid,
  TextField,
  Typography,
  Select,
  MenuItem,
  useMediaQuery,
  InputLabel
} from "@mui/material";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";

import axios from "axios";
import { toast } from "react-toastify";
import Loading from "../loading/loading";

import "./hcaptcha.css";

const siteKey = process.env.REACT_APP_HCAPTCHA_SITE_KEY;

export const HCaptchaForm = function () {
  const [captchaVerified, setCaptchaVerified] = useState(false);
  const [captchaToken, setCaptchaToken] = useState("");
  const [chainId, setChainId] = useState(null);
  const [walletAddress, setWalletAddress] = useState("");
  const [tokenAddress, setTokenAddress] = useState("");
  const [enabledTokens, setEnabledTokens] = useState([]);
  const [tokenAmount, setTokenAmount] = useState(0);
  const [showLoading, setShowLoading] = useState(false);

  const getFaucetInfo = async () => {
    return axios.get(`${process.env.REACT_APP_FAUCET_API_URL}/info`);
  };

  useEffect(() => {
    getFaucetInfo()
      .then((response) => {
        setChainId(response.data.chainId);
        setEnabledTokens(response.data.enabledTokens);
        setTokenAmount(response.data.maximumAmount);
      })
      .catch((error) => {
        toast.error(error);
      });
  }, []);

  const handleWalletAddressChange = (event) => {
    setWalletAddress(event.target.value);
  };

  const handleTokenChange = (event) => {
    setTokenAddress(event.target.value);
  };

  const isTabletOrMobile = useMediaQuery("(max-width:960px)");

  const onVerifyCaptcha = (_token) => {
    setCaptchaVerified(true);
    setCaptchaToken(_token);
  };

  function formatErrors(errors) {
    const divs = []
  
    for(let idx in errors) {
      divs.push(<div key={idx}>{errors[idx]}</div>)
    }

    return (
      <div>{divs}</div>
    )
  }

  const ToastTxSuccessful = (txHash) => (
    <div>
      Tokens sent to your wallet address. Hash: {txHash}
    </div>
  );

  const sendRequest = async () => {
    if (walletAddress.length <= 0) {
      toast.error("Please provide a wallet address.");
      return;
    }

    const apiURL = `${process.env.REACT_APP_FAUCET_API_URL}/ask`;
    try {
      setShowLoading(true);
      const req = {
        recipient: walletAddress,
        captcha: captchaToken,
        tokenAddress: tokenAddress,
        chainId: chainId,
        amount: tokenAmount,
      };

      axios
        .post(apiURL, req)
        .then((response) => {
          setShowLoading(false);
          setWalletAddress("");
          setCaptchaVerified(true);
          toast(ToastTxSuccessful(response.data.transactionHash));
        })
        .catch((error) => {
          setShowLoading(false);
          toast.error(formatErrors(error.response.data.errors));
        });
    } catch (error) {
      setShowLoading(false);
      if (error instanceof Error) {
        toast.error(error.message);
      }
    }
  };

  const showCaptcha = () => {
    return (
      <Fragment>
        <Grid item xs={12}>
          <Typography
            color="white"
            variant="body1"
            fontFamily="GT-Planar"
            fontSize="20px"
          >
            Verify
          </Typography>
        </Grid>
        <Grid item xs={12}>
          <HCaptcha
            size={isTabletOrMobile ? "compact" : "normal"}
            sitekey={siteKey}
            onVerify={onVerifyCaptcha}
          />
        </Grid>
      </Fragment>
    );
  };


  return (
    <Container maxWidth="sm">

      <Typography
        variant="h3"
        component="h2"
        align="center"
        gutterBottom={true}>
        Gnosis Faucet
      </Typography>

      <Typography
        variant="body1"
        component="h2"
        align="left"
        gutterBottom={true}>
        Paste your account address in the field below and choose if you want to receive either a portion of the native token or any of the enabled ERC20 tokens.
      </Typography>

      <Card>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <InputLabel id="input-wallet-address-label">Wallet address</InputLabel>
              <TextField
                onChange={handleWalletAddressChange}
                value={walletAddress}
                id="wallet-address"
                labelId="input-wallet-address-label"
                fullWidth
              />
            </Grid>
            <Grid item xs={12}>
              <InputLabel id="select-token-label">Token</InputLabel>
              <Select value={tokenAddress} onChange={handleTokenChange} labelId="select-token-label">
                {enabledTokens?.map((item) => {
                  return (
                    <MenuItem key={item.address} value={item.address}>
                      {item.name}
                    </MenuItem>
                  );
                })}
              </Select>
            </Grid>
            <Grid item xs={12}>
              <Button
                disabled={!captchaVerified || !walletAddress}
                variant="outlined"
                onClick={() => sendRequest()}
              >
                Claim
              </Button>
            </Grid>
            <Grid item xs={12}>
              {showCaptcha()}
            </Grid>
          </Grid>
        </CardContent>
      </Card>
      <Loading open={showLoading} />
    </Container>
  );
};
