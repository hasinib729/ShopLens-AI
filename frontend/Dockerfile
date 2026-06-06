FROM node:18-alpine

WORKDIR /app

# Copy package descriptors
COPY package.json /app/

# Install packages
RUN npm install

# Copy source code
COPY . /app/

# Expose Vite port
EXPOSE 5173

# Start development server binding to all network interfaces
CMD ["npm", "run", "dev", "--", "--host"]
