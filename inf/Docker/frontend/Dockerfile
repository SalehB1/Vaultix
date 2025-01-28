FROM node:20 AS build
WORKDIR /app
COPY ./frontend .
RUN ls -ltrh
RUN npm install -g npm@10.2.3
RUN npm i
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=build /app/dist /app/dist
EXPOSE 3000
RUN npm install -g serve
CMD ["serve", "-s", "dist", "-l", "3000"]

