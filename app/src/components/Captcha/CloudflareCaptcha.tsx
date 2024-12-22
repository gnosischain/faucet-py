import React from "react"
import Turnstile from "react-turnstile";

const siteKey = process.env.REACT_APP_CAPTCHA_SITE_KEY || "10000000-ffff-ffff-ffff-000000000001"

interface CaptchaProps {
  setCaptchaToken: (token: string) => void,
  // windowWidth: number,
  // captchaRef: null
}

const CloudflareCaptchaWidget: React.FC<CaptchaProps> = ({ setCaptchaToken }) => {
 
  const onVerifyCaptcha = (token: string) => {
    console.log(token)
    setCaptchaToken(token)
  }

  return (
    <Turnstile
      size="compact"
      sitekey={siteKey}
      onVerify={onVerifyCaptcha}
    />
  )
}

export default CloudflareCaptchaWidget
