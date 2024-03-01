/* eslint-disable */

import React, { useRef, useState, useEffect } from "react";
import HCaptcha from "@hcaptcha/react-hcaptcha"

const siteKey = process.env.REACT_APP_HCAPTCHA_SITE_KEY || "10000000-ffff-ffff-ffff-000000000001"

interface CaptchaProps {
  setCaptchaToken: (token: string) => void
}

// type CaptchaSize = "compact" | "normal" | "invisible"

const Captcha: React.FC<CaptchaProps> = ({ setCaptchaToken }) => {
  const captchaRef = useRef<HCaptcha>(null)

  const [windowWidth, setWindowWidth] = useState(window.innerWidth);

  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth)
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])
 
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
