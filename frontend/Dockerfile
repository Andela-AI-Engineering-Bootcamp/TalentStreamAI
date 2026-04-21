FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

EXPOSE 3000

# Bind all interfaces so host port mapping works; avoid `npm run dev` here because
# package.json uses dotenv with `../.env`, which does not exist at `/` inside this image.
CMD ["npx", "next", "dev", "-H", "0.0.0.0", "-p", "3000"]