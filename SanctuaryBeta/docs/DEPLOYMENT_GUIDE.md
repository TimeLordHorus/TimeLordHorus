# Sanctuary Beta - Deployment Guide

**Distribution URLs and Deployment Options**

---

## 📍 Local Access (Development)

### Find Your IP Address

```bash
# Run the helper script
./find-ip.sh

# Or manually:
# Linux/Mac:
hostname -I
ifconfig | grep "inet "

# Windows:
ipconfig
```

### Access URLs

**Same Computer:**
```
http://localhost:8080
```

**Meta Quest 3 (same WiFi):**
```
http://192.168.1.XXX:8080
# Replace XXX with your actual IP
```

**Example:**
```
http://192.168.1.105:8080
```

---

## 🚀 Public Deployment Options

### Option 1: Cloud Hosting (Recommended)

#### AWS Elastic Beanstalk

**Distribution URL:** `https://sanctuary-vr.us-east-1.elasticbeanstalk.com`

```bash
# Install AWS CLI and EB CLI
pip install awsebcli

# Initialize
eb init sanctuary-beta --platform java-17 --region us-east-1

# Create environment
eb create sanctuary-production

# Deploy
eb deploy

# Get URL
eb status
```

**Your URL will be:**
```
https://sanctuary-beta-env.xxxxxx.us-east-1.elasticbeanstalk.com
```

**Custom Domain:**
```
https://sanctuary.yourdomain.com
```

#### Google Cloud Platform (App Engine)

**Distribution URL:** `https://sanctuary-vr.appspot.com`

```bash
# Create app.yaml
cat > app.yaml << EOF
runtime: java17
instance_class: F4
env_variables:
  SPRING_PROFILES_ACTIVE: production
EOF

# Deploy
gcloud app deploy

# Get URL
gcloud app browse
```

**Your URL will be:**
```
https://PROJECT_ID.appspot.com
```

#### Azure App Service

**Distribution URL:** `https://sanctuary-vr.azurewebsites.net`

```bash
# Create resource group
az group create --name sanctuary-rg --location eastus

# Create App Service plan
az appservice plan create --name sanctuary-plan --resource-group sanctuary-rg --sku B1 --is-linux

# Create web app
az webapp create --resource-group sanctuary-rg --plan sanctuary-plan --name sanctuary-vr --runtime "JAVA:17-java17"

# Deploy
az webapp deployment source config-zip --resource-group sanctuary-rg --name sanctuary-vr --src target/sanctuary-beta-0.1.0-BETA.jar

# Get URL
az webapp show --name sanctuary-vr --resource-group sanctuary-rg --query defaultHostName
```

**Your URL will be:**
```
https://sanctuary-vr.azurewebsites.net
```

---

### Option 2: VPS / Dedicated Server

**Providers:** DigitalOcean, Linode, Vultr, Hetzner

#### DigitalOcean Droplet

**Distribution URL:** `https://sanctuary.your-domain.com`

```bash
# 1. Create droplet (Ubuntu 22.04)
# 2. SSH into server
ssh root@YOUR_DROPLET_IP

# 3. Install Java
apt update
apt install openjdk-17-jdk -y

# 4. Upload JAR
scp target/sanctuary-beta-0.1.0-BETA.jar root@YOUR_DROPLET_IP:/opt/sanctuary/

# 5. Create systemd service
cat > /etc/systemd/system/sanctuary.service << EOF
[Unit]
Description=Sanctuary VR Beta
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/sanctuary
ExecStart=/usr/bin/java -jar /opt/sanctuary/sanctuary-beta-0.1.0-BETA.jar
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# 6. Start service
systemctl enable sanctuary
systemctl start sanctuary

# 7. Setup Nginx reverse proxy
apt install nginx certbot python3-certbot-nginx -y

cat > /etc/nginx/sites-available/sanctuary << EOF
server {
    listen 80;
    server_name sanctuary.yourdomain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF

ln -s /etc/nginx/sites-available/sanctuary /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# 8. Get SSL certificate
certbot --nginx -d sanctuary.yourdomain.com
```

**Your URL will be:**
```
https://sanctuary.yourdomain.com
```

---

### Option 3: Docker Deployment

#### Docker Hub + Cloud Run

**Distribution URL:** `https://sanctuary-vr-xxxxx.run.app`

```bash
# 1. Build and push to Docker Hub
docker build -t yourusername/sanctuary-beta:latest .
docker push yourusername/sanctuary-beta:latest

# 2. Deploy to Google Cloud Run
gcloud run deploy sanctuary-vr \
  --image yourusername/sanctuary-beta:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Get URL
gcloud run services describe sanctuary-vr --region us-central1 --format 'value(status.url)'
```

**Your URL will be:**
```
https://sanctuary-vr-xxxxx-uc.a.run.app
```

#### AWS ECS (Fargate)

```bash
# Push to Amazon ECR
aws ecr create-repository --repository-name sanctuary-beta
docker tag sanctuary-beta:latest ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/sanctuary-beta:latest
docker push ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/sanctuary-beta:latest

# Deploy to ECS
# Use AWS Console or CLI to create ECS service
```

---

### Option 4: Serverless (Heroku)

**Distribution URL:** `https://sanctuary-vr.herokuapp.com`

```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Create app
heroku create sanctuary-vr

# Deploy
git push heroku main

# Get URL
heroku open
```

**Your URL will be:**
```
https://sanctuary-vr.herokuapp.com
```

**Note:** Heroku no longer has a free tier, starts at $5/month.

---

### Option 5: Tunnel for Testing (ngrok)

**Temporary URL for Quest 3 testing without deployment**

```bash
# Install ngrok
# Download from https://ngrok.com

# Start Sanctuary
./run.sh

# In another terminal, create tunnel
ngrok http 8080
```

**You'll get a temporary URL:**
```
https://xxxx-xx-xx-xxx-xxx.ngrok-free.app
```

**Access from Quest 3:**
- Open Quest Browser
- Navigate to ngrok URL
- Click "Enter VR"

**⚠️ Warning:** ngrok URLs are temporary and change each time!

---

## 🌐 Recommended Distribution URLs

### For Production:

**Best Options:**
1. **Custom Domain + VPS:**
   ```
   https://sanctuary.vr
   https://enter.sanctuary.vr
   https://beta.sanctuary.vr
   ```

2. **Cloud Platform:**
   ```
   https://sanctuary.app
   https://sanctuaryvr.app
   ```

### For Beta Testing:

```
https://beta.sanctuary.yourdomain.com
https://sanctuary-beta.herokuapp.com
https://sanctuary.vercel.app
```

---

## 🔒 HTTPS Requirements

**WebXR requires HTTPS** (except localhost)!

### Get Free SSL Certificate:

**Option 1: Let's Encrypt (certbot)**
```bash
certbot --nginx -d sanctuary.yourdomain.com
```

**Option 2: Cloudflare**
- Point domain to your server
- Enable Cloudflare proxy
- Auto SSL enabled

**Option 3: Cloud platforms**
- AWS, GCP, Azure provide free SSL
- Auto-configured

---

## 📊 Cost Estimates

| Platform | Monthly Cost | SSL | URL |
|----------|-------------|-----|-----|
| **ngrok (free)** | $0 | ✅ | Temporary |
| **Heroku Eco** | $5 | ✅ | Custom domain |
| **DigitalOcean** | $6 | 🔧 | Custom domain |
| **AWS Lightsail** | $5 | 🔧 | Custom domain |
| **Google Cloud Run** | $5-20 | ✅ | Auto-generated |
| **AWS Beanstalk** | $10-30 | 🔧 | Auto-generated |
| **Azure App Service** | $13+ | ✅ | Auto-generated |

🔧 = Manual setup required
✅ = Automatic

---

## 🎯 Quick Start Recommendation

**For immediate Quest 3 testing:**

1. **Use ngrok (5 minutes):**
   ```bash
   # Terminal 1
   cd SanctuaryBeta
   ./run.sh

   # Terminal 2
   ngrok http 8080
   # Copy the HTTPS URL
   ```

2. **Access from Quest 3:**
   - Open Quest Browser
   - Go to ngrok URL
   - Enter VR!

**For permanent deployment:**

1. **Buy domain:** sanctuary.vr, sanctuaryvr.com, etc.
2. **Deploy to DigitalOcean:**
   - $6/month droplet
   - Setup with guide above
   - SSL with certbot
3. **Point domain to server**
4. **Access:** `https://sanctuary.yourdomain.com`

---

## 🚀 Example Full Deployment

```bash
# 1. Build
cd SanctuaryBeta
mvn clean package

# 2. Setup server (DigitalOcean/AWS/Azure)
# Create Ubuntu 22.04 server

# 3. Deploy
scp target/sanctuary-beta-0.1.0-BETA.jar root@YOUR_SERVER:/opt/sanctuary/
ssh root@YOUR_SERVER

# 4. Install Java & setup service (see VPS section above)

# 5. Configure domain
# Point A record: sanctuary.yourdomain.com -> SERVER_IP

# 6. Setup Nginx + SSL (see above)

# 7. Done! Access at:
# https://sanctuary.yourdomain.com
```

---

## 📱 Quest 3 Access

Once deployed, users access via:

1. **Put on Quest 3**
2. **Open Quest Browser**
3. **Navigate to:**
   ```
   https://sanctuary.yourdomain.com
   ```
4. **Click "Enter VR"**
5. **Experience Sanctuary!**

**No app installation required!** 🎉

---

## 🔧 Domain Setup

### Buy a Domain:

**Registrars:**
- Namecheap: ~$10/year
- Google Domains: ~$12/year
- Cloudflare: ~$10/year
- GoDaddy: ~$15/year

**Recommended domains:**
- `sanctuary.vr` (if available)
- `sanctuaryvr.com`
- `sanctuary.app`
- `entersanctuary.com`

### DNS Configuration:

```
Type: A Record
Name: @ (or sanctuary)
Value: YOUR_SERVER_IP
TTL: Automatic
```

**Example:**
```
A    sanctuary.yourdomain.com    →  165.227.xxx.xxx
A    beta.sanctuary.yourdomain.com  →  165.227.xxx.xxx
```

---

## 📈 Scaling

**As users grow:**

1. **Start:** Single server ($6/month)
2. **Medium:** Load balancer + 2 servers ($30/month)
3. **Large:** Kubernetes cluster ($100+/month)
4. **Enterprise:** Multi-region deployment

**Database:**
1. **Start:** PostgreSQL on same server
2. **Medium:** Managed database (AWS RDS, $15/month)
3. **Large:** Read replicas + caching
4. **Enterprise:** Multi-region, sharding

---

## ✅ Final Recommendation

**Best Setup for Sanctuary Beta:**

```
Domain:     sanctuary.vr (or .com)
Hosting:    DigitalOcean Droplet ($6/month)
Database:   PostgreSQL (on same server)
SSL:        Let's Encrypt (free)
CDN:        Cloudflare (free tier)

Total: ~$16/month (server + domain)

Distribution URL: https://sanctuary.vr
```

This gives you:
- Professional custom domain
- Full control
- Easy to scale
- Quest 3 compatible
- PWA installable

---

## Need Help?

If you need assistance with deployment, let me know which platform you'd like to use!
