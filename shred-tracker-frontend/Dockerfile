# 1. 使用 Node 镜像作为基础
FROM node:18

# 2. 设置容器内的工作目录
WORKDIR /app

# 3. 只复制 package.json 相关文件，先安装依赖（利用 Docker 缓存）
COPY package*.json ./
RUN npm install

# 4. 复制前端所有源代码
COPY . .

# 5. 暴露 Vite 默认的 5173 端口
EXPOSE 5173

# 6. 启动开发服务器，注意必须加 --host 0.0.0.0
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]