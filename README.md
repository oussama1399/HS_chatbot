# HS Chatbot - Assistant IA pour Service de Traiteur

## 🍽️ Description

HS Chatbot est un assistant IA intelligent conçu spécialement pour les services de traiteur HS Traiteur. Il utilise Google Gemini pour fournir des réponses contextuelles et personnalisées aux clients concernant les produits, services, et aide à la qualification des commandes.

## ✨ Fonctionnalités

### 🤖 Agent IA Intelligent
- **Traitement du langage naturel** en français
- **Réponses contextuelles** basées sur l'historique de conversation
- **Moteur de recommandations** personnalisé
- **Qualification automatique** des demandes clients

### 📊 Intégration de Données
- **Base de données vectorielle** ChromaDB pour recherche sémantique
- **Catalogue produits** avec plus de 30 articles
- **Services spécialisés** : mariages, soutenances, buffets
- **Gestion de sessions** persistante

### 🎨 Interface Utilisateur
- **Design responsive** avec Bootstrap 5
- **Chat en temps réel** avec WebSocket
- **Actions rapides** pour navigation intuitive
- **Suggestions de produits** visuelles

## 🚀 Installation

### Prérequis
- Python 3.8+
- Node.js (pour les dépendances frontend)
- Clé API Google Gemini

### 1. Clonage et Installation
```bash
git clone <repository-url>
cd hs-chatbot
pip install -r requirements.txt
```

### 2. Configuration
Créez un fichier `.env` avec vos clés API :
```env
GOOGLE_API_KEY=votre-clé-api-gemini
ENVIRONMENT=development
SESSION_TIMEOUT=1800
CHROMA_PERSIST_DIRECTORY=./chroma_db
FLASK_SECRET_KEY=votre-clé-secrète
```

### 3. Initialisation des Données
```bash
python run.py
```

## 🏗️ Architecture

### Structure du Projet
```
hs-chatbot/
├── main.py                 # Application Flask principale
├── run.py                  # Script de démarrage
├── requirements.txt        # Dépendances Python
├── config.json            # Configuration application
├── .env                   # Variables d'environnement
├── data/                  # Données et templates
│   ├── products_rag.csv   # Catalogue produits
│   ├── services_rag.csv   # Services disponibles
│   ├── sessions.json      # Sessions utilisateur
│   └── prompt_templates/  # Templates de prompts
├── utils/                 # Utilitaires et logique métier
│   ├── data_loader.py     # Chargement des données
│   ├── session_manager.py # Gestion des sessions
│   ├── vector_db.py       # Base de données vectorielle
│   └── prompt_engineer.py # Ingénierie des prompts
├── templates/             # Templates HTML
│   ├── index.html         # Interface chat principale
│   ├── 404.html          # Page d'erreur 404
│   └── 500.html          # Page d'erreur 500
├── static/               # Ressources statiques
│   ├── css/style.css     # Styles personnalisés
│   └── js/app.js         # JavaScript application
└── tests/                # Tests unitaires
    └── test_components.py
```

### 🔧 Composants Principaux

#### 1. **DataLoader** (`utils/data_loader.py`)
- Chargement et traitement des données CSV
- Recherche dans le catalogue produits
- Filtrage par catégorie, prix, disponibilité

#### 2. **SessionManager** (`utils/session_manager.py`)
- Gestion des sessions utilisateur
- Historique des conversations
- Contexte utilisateur persistant

#### 3. **VectorDatabase** (`utils/vector_db.py`)
- Intégration ChromaDB
- Recherche sémantique avancée
- Embeddings avec Sentence Transformers

#### 4. **PromptEngineer** (`utils/prompt_engineer.py`)
- Génération de réponses avec Gemini
- Contextualisation des prompts
- Extraction d'intentions utilisateur

## 🎯 Utilisation

### Démarrage de l'Application
```bash
python run.py
```

### Interface Web
Accédez à `http://localhost:5000` pour utiliser l'interface chat.

### API Endpoints
- `GET /api/health` - Vérification de l'état
- `GET /api/stats` - Statistiques de l'application
- `GET /api/products` - Liste des produits
- `GET /api/services` - Liste des services
- `GET /api/search?q=terme` - Recherche produits/services

### WebSocket Events
- `connect` - Connexion utilisateur
- `message` - Envoi de message
- `get_suggestions` - Demande de suggestions
- `typing` - Indicateur de saisie

## 🧪 Tests

### Tests Unitaires
```bash
python -m pytest tests/ -v
```

### Tests des Composants
```bash
python tests/test_components.py
```

## 🔐 Sécurité

### Bonnes Pratiques Implémentées
- ✅ Variables d'environnement pour les clés API
- ✅ Validation des entrées utilisateur
- ✅ Gestion des erreurs robuste
- ✅ Sessions sécurisées
- ✅ CORS configuré

### Recommandations
- Ne jamais committer le fichier `.env`
- Utiliser HTTPS en production
- Implémenter la limitation de taux (rate limiting)
- Monitorer les logs d'erreur

## 📈 Monitoring et Statistiques

### Métriques Disponibles
- Nombre de sessions actives
- Messages échangés
- Produits les plus consultés
- Performance des requêtes

### Logs
Les logs sont sauvegardés dans `hs_chatbot.log` et affichés dans la console.

## 🚀 Déploiement

### Production avec Gunicorn
```bash
gunicorn --worker-class eventlet -w 1 main:app
```

### Variables d'Environnement Production
```env
ENVIRONMENT=production
PORT=5000
GOOGLE_API_KEY=votre-clé-production
```


## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

**Développé avec ❤️ pour HS Traiteur**
