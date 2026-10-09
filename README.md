# Lucky Draw Offers

A shared server-backed lucky draw app with fixed prize limits and an admin reset PIN.

## Prize limits
- 15% Discount: 6
- 10% Discount: 10
- 5% Discount: 20
- Free Earrings: 20
- Free T-light Holder: 30
- Total: 86 draws

The app weights each draw by the remaining number of each prize, so each remaining prize slot has an equal chance. Counts are shared across visitors and saved in SQLite. The admin reset resets all counts to zero.

## Deploy to Render
1. Create a GitHub repository and upload these files/folders (`app.py`, `requirements.txt`, `render.yaml`, and `templates/index.html`).
2. In Render, choose **New + → Blueprint**, connect the repository, and deploy.
3. Set the `ADMIN_PIN` environment variable to a private PIN of your choice in Render. Do not keep the default PIN `2468`.
4. After deployment, Render gives you a public `https://...onrender.com` URL to share.

The included Render configuration mounts a persistent disk for SQLite. Check the host's current free-plan/disk terms before deploying; persistent disks may require a paid plan.

## Run locally
```bash
pip install -r requirements.txt
ADMIN_PIN=your-private-pin python app.py
```
Open `http://localhost:5000`.

## Important
Anyone can draw an offer, but reset is protected by the admin PIN. Keep that PIN private. For real promotional use, display the terms and conditions for each offer.
