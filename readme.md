# Star Roll

English | [中文](./readme_zh.md)

**StarRoll** is a mobile stargazing app built around the Hipparcos star catalog (HIP). Point your phone at the sky to explore an AR star map, identify stars from photos, and connect with other stargazers — every blog, chat room, and message is anchored to a real star.

## Preview

**Find a star in AR** — the arrow guides you toward the target star; once it enters the view it gets highlighted, and tapping it opens the star details card:

| 1. Follow the arrow | 2. Star highlighted | 3. Star details |
| :---: | :---: | :---: |
| <img src="./preview/find_star_step1.png" alt="Follow the arrow to the target star" width="260" /> | <img src="./preview/find_star_step2.png" alt="Target star highlighted in AR view" width="260" /> | <img src="./preview/find_star_step3.png" alt="Star details card for Betelgeuse" width="260" /> |

**Photo star recognition & star trail simulation**:

| Photo star recognition | Star trail simulation |
| :---: | :---: |
| <img src="./preview/reconize_star.png" alt="Stars identified and annotated on an uploaded photo" width="260" /> | <img src="./preview/star_trail_preview.png" alt="Simulated long-exposure star trails" width="260" /> |

## Features

- **AR Star Map** — Live camera view overlaid with the real-time night sky (stars, constellations, nebula background), driven by GPS, device orientation sensors, and astronomical coordinate transforms. Supports time travel (fixed / accelerated time) and custom observer location.
- **Star Trail Simulation** — Generate long-exposure style star trail images with configurable duration, interval, and brightness.
- **Photo Star Recognition** — Upload a photo of the night sky and identify the stars in it via a self-hosted [astrometry.net](http://astrometry.net/) plate-solving engine, with results annotated on the original image.
- **Search & Find-Star Guidance** — Search stars by common name, then let the on-screen arrow guide you to the target star in AR.
- **Star Messages** — Leave a message on a star and share it via link; the recipient finds the star in AR to read it.
- **Star Blogs** — Each star has its own blog space with posts, likes, comments, saves, and reports.
- **Star Chat Rooms** — Real-time chat room per star over WebSocket, backed by Redis Pub/Sub and Kafka.
- **User System & Achievements** — Registration, JWT login, email-based password reset, profile editing, star discovery ranks (Novice → Explorer → Astronomer → Star Lord).
- **Stargazing Recommendations** — Periodic emails recommending the best nearby observation site based on weather and light pollution.

## Architecture

```
Client (Vue 3 + Three.js)
   │ REST (OpenAPI)            │ WebSocket (chat)
   ▼                           ▼
Console Service (FastAPI, multi-instance)
   ├── MySQL          — users, blogs, chats, jobs, discoveries
   ├── Redis          — verification codes, chat Pub/Sub
   ├── Kafka          — async chat message persistence
   ├── MinIO / S3     — image storage
   └── astrometry.net — plate solving
Cronjob Service
   ├── star identification job scheduler
   └── stargazing recommendation emails
```

**Functional architecture**:

<img src="./preview/Functional%20architecture%20diagram.png" alt="Functional architecture diagram" width="800" />

**Technical architecture**:

<img src="./preview/Technical%20architecture%20diagram.png" alt="Technical architecture diagram" width="800" />

All HTTP APIs are defined in [`idl/openapiv3.yaml`](./idl/openapiv3.yaml) as the single source of truth; both server stubs (python-fastapi) and client SDKs (typescript-fetch) are generated from it.

## Getting Started

- Development workflow and code generation: [`for_developer.md`](./for_developer.md)
- Backend architecture, standards, and local environment setup (MySQL / Redis / Kafka / MinIO / astrometry.net): [`backend/for_backend_developer.md`](./backend/for_backend_developer.md)
- Kubernetes deployment guide: [`k8s/readme.md`](./k8s/readme.md)

### Frontend

```bash
cd frontend/vue-app
npm install
npm run dev
```

### Backend

```bash
pip install -r backend/requirements.txt
# configure .env, then start the console service (see backend docs)
```

## Contributors

- Qiming Cao
- Songcheng Gao
- Yuhui Cao
- Sahil Sabir
- Kehan Liu
- Tianlai Gu
- Huafu Fang
- Shuyu He
