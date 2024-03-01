import { useEffect, useState } from "react";
import logo from "./images/logo.svg"
import "./css/App.css";
// import { HCaptchaForm } from "./components/hcaptcha/hcaptcha";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import axios from "axios";
import Loading from "./components/Loading/Loading";
import Faucet from "./components/FaucetForm/Faucet";

const chainName:{ [key: string]: string }= {
  "100": "Gnosis",
  "10200": "Chiado"
}

function App(): JSX.Element {
  const [chainId, setChainId] = useState("10200");
  const [loading, setLoading] = useState(true)
  // const [enabledTokens, setEnabledTokens] = useState([]);

  const getFaucetInfo = async () => {
    return axios.get(`${process.env.REACT_APP_FAUCET_API_URL}/info`);
  };


  useEffect(() => {
    getFaucetInfo()
      .then((response) => {
        setChainId(response.data.chainId);
        // setEnabledTokens(response.data.enabledTokens);
      })
      .catch(() => {
        toast.error("Network error");
      })
      .finally(() => {
        // setTimeout(()=> {setLoading(false)}, 5000)
        setLoading(false);
      });
  }, []);

  const title = loading ? "CHAIN" : `${chainName[chainId]} CHAIN`
  const subtitle = loading
    ? "Loading faucet..."
    : (chainId === "100" ? "Faucet" : "Testnet Faucet")

  const enabledTokens = [
    {
      address: "0x01",
      name: "GNO",
      maximumAmount: 2,
    },
    {
      address: "0x02",
      name: "xDAI",
      maximumAmount: 10,
    }
  ]
  
  return (
    <>
      <ToastContainer
        position="top-right"
        autoClose={false}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick={false}
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />
      {loading && <Loading/>}
      <div className="app-container">
        <img src={logo} className="app-logo" alt="logo" />
        <div className="title">
          <h1>{title}</h1>
          <h2>{subtitle}</h2>
        </div>
        <Faucet enabledTokens={enabledTokens}/>
        {/* <HCaptchaForm/> */}
      </div>
    </>
  );
}

export default App;
