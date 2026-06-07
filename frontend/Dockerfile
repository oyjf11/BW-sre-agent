FROM registry.cn-hangzhou.aliyuncs.com/acs/node:20-alpine AS builder

WORKDIR /app

COPY package*.json .
RUN npm ci --registry=https://registry.npmmirror.com

ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

COPY . .
RUN npm run build

FROM registry.cn-hangzhou.aliyuncs.com/acs/nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
