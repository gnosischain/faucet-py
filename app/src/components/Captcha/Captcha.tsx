import React, { RefObject } from "react"
import HCaptcha from "@hcaptcha/react-hcaptcha"

const siteKey = process.env.REACT_APP_HCAPTCHA_SITE_KEY || "10000000-ffff-ffff-ffff-000000000001"

interface CaptchaProps {
  setCaptchaToken: (token: string) => void,
  windowWidth: number,
  captchaRef: RefObject<HCaptcha>
}

const Captcha: React.FC<CaptchaProps> = ({ setCaptchaToken, windowWidth, captchaRef }) => {
 
  const onVerifyCaptcha = (token: string) => {
    setCaptchaToken(token)
  }

  return (
    <HCaptcha
      size={windowWidth > 500 ? "normal" : "compact"}
      sitekey={siteKey}
      onVerify={onVerifyCaptcha}
      ref={captchaRef}
    />
  )
}

export default Captcha
