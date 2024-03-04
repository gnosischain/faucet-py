import { useEffect, useState } from "react"
import { ToastContainer, toast } from "react-toastify"
import "react-toastify/dist/ReactToastify.css"
import axios from "axios"
import logo from "./images/logo.svg"
import "./css/App.css"
import Loading from "./components/Loading/Loading"
import Faucet from "./components/FaucetForm/Faucet"

const chainName:{ [key: string]: string }= {
  "100": "Gnosis",
  "10200": "Chiado"
}

function App(): JSX.Element {
  const [chainId, setChainId] = useState("10200")
  const [loading, setLoading] = useState(true)
  const [enabledTokens, setEnabledTokens] = useState([])
  const [faucetLoading, setFaucetLoading] = useState(true)

  const getFaucetInfo = async () => {
    return axios.get(`${process.env.REACT_APP_FAUCET_API_URL}/info`)
  }

  // console.log(enabledTokens.length)

  useEffect(() => {
    getFaucetInfo()
      .then((response) => {
        setChainId(response.data.chainId)
        setEnabledTokens(response.data.enabledTokens)
      })
      .catch(() => {
        toast.error("Network error")
      })
      .finally(() => {
        // setTimeout(()=> {
        //   setLoading(false)
        //   setFaucetLoading(false)
        // }, 2000)
        setFaucetLoading(false)
        setLoading(false)
      })
  }, [])

  const title = faucetLoading ? "FAUCET" : `${chainName[chainId]} CHAIN`
  const subtitle = faucetLoading
    ? "Loading..."
    : (chainId === "100" ? "Faucet" : "Testnet Faucet")

  // const enabledTokens1 = [
  //   {
  //     address: "0x01",
  //     name: "GNO",
  //     maximumAmount: 2,
  //   },
  //   {
  //     address: "0x02",
  //     name: "xDAI",
  //     maximumAmount: 10,
  //   }
  // ]
  
  return (
    <>
      <ToastContainer
        position="bottom-right"
        hideProgressBar={true}
        newestOnTop={false}
        closeOnClick={true}
        // pauseOnFocusLoss
        draggable
        pauseOnHover
      />
      <div className="app-container">
        <img src={logo} className="app-logo" alt="logo" />
        <div className="title">
          <h1>{title}</h1>
          <h2>{subtitle}</h2>
        </div>
        <Faucet
          chainId={chainId}
          enabledTokens={enabledTokens}
          setLoading={setLoading}
        />
      </div>
      {loading && <Loading/>}
    </>
  )
}

export default App
