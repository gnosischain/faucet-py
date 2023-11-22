import logo from "./images/logo.svg";
import "./css/App.css";
import { HCaptchaForm } from "./components/hcaptcha/hcaptcha";

import { Fragment } from "react";
import { Container } from "@mui/system";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

function App() {
  return (
    <Fragment>
      <Container maxWidth="xl" sx={{ marginBottom: "2em" }} id="app-container">
        <ToastContainer
          position="top-right"
          autoClose={50000}
          hideProgressBar={false}
          newestOnTop={false}
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
        />

        <img src={logo} className="App-logo" alt="logo" />

        <HCaptchaForm></HCaptchaForm>
      </Container>
    </Fragment>
  );
}

export default App;
