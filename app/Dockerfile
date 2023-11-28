# Stage 1
FROM node:18.5.0-slim@sha256:ab9c000b5369548683617a64ced2eace8714b496abaeac9bd796266471ee65a7 as builder

WORKDIR app
COPY package.json .
COPY yarn.lock .
RUN yarn
COPY . .

ENV NODE_ENV production
ARG REACT_APP_HCAPTCHA_SITE_KEY
ARG REACT_APP_FAUCET_API_URL
ENV REACT_APP_HCAPTCHA_SITE_KEY ${REACT_APP_HCAPTCHA_SITE_KEY}
ENV REACT_APP_FAUCET_API_URL ${REACT_APP_FAUCET_API_URL}
RUN yarn build

# Stage 2
FROM nginx:1.25.3@sha256:3c4c1f42a89e343c7b050c5e5d6f670a0e0b82e70e0e7d023f10092a04bbb5a7
WORKDIR /usr/share/nginx/html
RUN rm -rf ./*
COPY --from=builder /app/build .
ENTRYPOINT ["nginx", "-g", "daemon off;"]