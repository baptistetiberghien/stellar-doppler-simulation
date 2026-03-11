# Déployer sur Vercel

Ce projet a **deux parties** : un **frontend** (Vue/Vite) et un **backend** (FastAPI/Python). Voici comment les déployer, avec le frontend sur Vercel.

---

## Option 1 : Frontend sur Vercel + Backend ailleurs (recommandé)

Le frontend est hébergé sur Vercel. Le backend tourne sur un autre service (Railway, Render, Fly.io, etc.).

### 1. Déployer le frontend sur Vercel

**Depuis le tableau de bord Vercel :**

1. Allez sur [vercel.com](https://vercel.com) et connectez votre dépôt Git (GitHub, GitLab, Bitbucket).
2. **Import** du projet : choisissez le repo `stellar-doppler-simulation`.
3. **Paramètres du projet** :
   - **Root Directory** : `frontend`  
     (obligatoire, car le frontend est dans le sous-dossier `frontend/`)
   - **Framework Preset** : Vite (détecté automatiquement)
   - **Build Command** : `npm run build`
   - **Output Directory** : `dist`
   - **Install Command** : `npm install`
4. **Variables d’environnement** (à ajouter dans *Settings → Environment Variables*) :
   - `VITE_API_URL` = l’URL de votre backend, **sans slash final**  
     Exemple : `https://votre-backend.railway.app` ou `https://votre-app.onrender.com`
5. Déployez (Deploy). Chaque push sur la branche configurée déclenchera un nouveau déploiement.

**En ligne de commande (Vercel CLI) :**

```bash
cd frontend
npm i -g vercel
vercel
```

Quand on vous demande le répertoire racine, indiquez `.` (vous êtes déjà dans `frontend/`). Puis ajoutez la variable `VITE_API_URL` dans le dashboard Vercel (Project → Settings → Environment Variables).

### 2. Déployer le backend

Le frontend appelle `VITE_API_URL/simulate`, `VITE_API_URL/simulate-advanced`, `VITE_API_URL/simulate-multispot`. Il faut donc un serveur qui expose ces routes.

**Exemple avec Railway :**

1. Créez un projet sur [railway.app](https://railway.app).
2. *New* → *GitHub Repo* → sélectionnez le même repo.
3. *Root Directory* : `backend` (ou déployez tout le repo et indiquez que la commande de démarrage est depuis `backend/`).
4. *Settings* : *Start Command* par exemple :  
   `pip install -r requirements.txt && python -m uvicorn main:app --host 0.0.0.0 --port $PORT`  
   (en adaptant si votre point d’entrée est `backend.main:app` selon la structure du repo).
5. Récupérez l’URL publique du service (ex. `https://xxx.railway.app`) et mettez-la dans `VITE_API_URL` sur Vercel.

**Exemple avec Render :**

1. [render.com](https://render.com) → *New* → *Web Service*.
2. Liez le repo, *Root Directory* : `backend`.
3. *Build* : `pip install -r requirements.txt`
4. *Start* : `uvicorn main:app --host 0.0.0.0 --port $PORT` (adapter si besoin `main:app` → `backend.main:app` selon votre structure).
5. Utilisez l’URL du service comme `VITE_API_URL` dans Vercel.

Après redéploiement du frontend (avec la bonne `VITE_API_URL`), le site sur Vercel utilisera ce backend.

---

## Option 2 : Tout sur Vercel (frontend + API en serverless)

On peut aussi faire tourner l’API FastAPI en **fonction serverless** Vercel (Python). Cela demande d’adapter le backend pour un handler serverless (ex. Mangum) et d’exposer les routes sous `/api`. Si vous voulez cette option, il faudra :

- Un handler dans `api/` qui wrap l’app FastAPI (ex. avec Mangum).
- Dépendances Python (y compris `numpy`) gérées par Vercel pour les fonctions.
- Configurer le frontend avec `VITE_API_URL` pointant vers le même domaine (ex. `/api`), pour que les appels aillent vers vos fonctions.

Pour l’instant, l’**Option 1** (frontend sur Vercel, backend sur Railway/Render) est la plus simple et la plus fiable.

---

## Vérifications

- **Root Directory** du projet Vercel = `frontend`.
- **Variables d’environnement** : `VITE_API_URL` défini en production (sinon les appels API partent vers le même domaine et échouent si l’API n’est pas sur Vercel).
- **Backend CORS** : le backend a déjà `allow_origins=["*"]`, donc votre domaine Vercel sera accepté.
- Après déploiement, tester les trois pages (Simple, Advanced, Stochastic) et le calcul du spectre pour confirmer que l’API répond.
