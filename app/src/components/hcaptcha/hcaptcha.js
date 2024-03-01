import { useEffect, useState, useRef, Fragment } from "react";
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
  FormControl,
  FormLabel
} from "@mui/material";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";

import axios from "axios";
import { toast } from "react-toastify";
import Loading from "../Loading/Loading";

import "./hcaptcha.css";

const siteKey = process.env.REACT_APP_HCAPTCHA_SITE_KEY;

export const HCaptchaForm = function () {
  const captchaRef = useRef(null);
  const [captchaVerified, setCaptchaVerified] = useState(false);
  const [captchaToken, setCaptchaToken] = useState("");
  const [chainId, setChainId] = useState(null);
  const [chainName, setChainName] = useState("");
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
        setChainName(response.data.chainName);
        setEnabledTokens(response.data.enabledTokens);
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

    // Set token amount
    for (let idx in enabledTokens) {
      if (enabledTokens[idx].address.toLowerCase() == event.target.value.toLowerCase()) {
        setTokenAmount(enabledTokens[idx].maximumAmount)
        break;
      }
    }
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
          // Reset captcha
          setCaptchaVerified(true);
          captchaRef.current?.resetCaptcha();
          // Show info on UI
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
            ref={captchaRef}
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
        {chainName} Faucet
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
              <FormControl fullWidth>
                <FormLabel component="legend">Wallet address</FormLabel>
                <TextField
                  onChange={handleWalletAddressChange}
                  value={walletAddress}
                  id="wallet-address"
                  labelid="input-wallet-address-label"
                  fullWidth
                />
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControl sx={{ minWidth: 120 }} size="small">
                <FormLabel component="legend">Choose token</FormLabel>
                <Select value={tokenAddress} onChange={handleTokenChange} labelid="select-token-label" autowidth="true">
                  {enabledTokens?.map((item) => {
                    return (
                      <MenuItem key={item.address} value={item.address}>
                        <b>{item.name}</b>&nbsp;{item.maximumAmount} day
                      </MenuItem>
                    );
                  })}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControl autowidth="true">
                <Button
                  disabled={!captchaVerified || !walletAddress}
                  variant="outlined"
                  onClick={() => sendRequest()}
                >
                  Claim
                </Button>
              </FormControl>
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
