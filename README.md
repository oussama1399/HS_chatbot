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
- **Catalogue produits** avec 29 articles
- **Services spécialisés** : mariages, soutenances, buffets (7 services)
- **Gestion de sessions** persistante
- **Chargement de données** optimisé avec CSV

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
python main.py
```

## 🏗️ Architecture

### Structure du Projet
```
hs-chatbot/
├── main.py                 # Application Flask principale
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
│   └── prompt_engineer.py # Ingénierie des prompts
├── templates/             # Templates HTML
│   ├── index.html         # Interface chat principale
│   ├── 404.html          # Page d'erreur 404
│   └── 500.html          # Page d'erreur 500
├── static/               # Ressources statiques
│   ├── css/style.css     # Styles personnalisés
│   └── js/app.js         # JavaScript application
├── data_preprocessing.ipynb # Notebook de préparation des données
├── datagen.ipynb          # Notebook de génération de données
└── models/               # Modèles et agents
    └── agents.ipynb      # Notebook d'agents IA
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

#### 3. **PromptEngineer** (`utils/prompt_engineer.py`)
- Génération de réponses avec Gemini
- Contextualisation des prompts
- Extraction d'intentions utilisateur

## 🎯 Utilisation

### Démarrage de l'Application
```bash
python main.py
```

### Interface Web
Accédez à `http://localhost:5000` pour utiliser l'interface chat.

### API Endpoints
- `GET /api/health` - Vérification de l'état
- `GET /api/stats` - Statistiques de l'application
- `GET /api/products` - Liste des produits
- `GET /api/services` - Liste des services

### WebSocket Events
- `connect` - Connexion utilisateur
- `message` - Envoi de message

## 🧪 Développement

### Notebooks de Développement
- `data_preprocessing.ipynb` - Préparation des données
- `datagen.ipynb` - Génération de données
- `models/agents.ipynb` - Développement des agents IA

### Démarrage Rapide
```bash
# Cloner le projet
git clone <repository-url>
cd hs-chatbot

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
# Éditer le fichier .env avec vos clés API

# Démarrer l'application
python main.py
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
Les logs sont affichés dans la console avec des informations détaillées sur le fonctionnement de l'application.

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

## 🤝 Contribution

### Développement
1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

### Guidelines
- Suivre PEP 8 pour le code Python
- Documenter les nouvelles fonctionnalités
- Utiliser des messages de commit descriptifs
- Tester les changements avant de les proposer

## 📞 Support

Pour toute question ou problème :
- Consultez la documentation
- Vérifiez les logs d'erreur dans la console
- Ouvrez une issue sur GitHub

## 🎯 Fonctionnalités Actuelles

### ✅ Implémentées
- Chat en temps réel avec WebSocket
- Réponses IA avec Google Gemini
- Gestion des produits et services (29 produits, 7 services)
- Interface utilisateur responsive
- Gestion des sessions utilisateur
- API REST pour l'intégration

### 🔄 En Développement
- Recherche sémantique avancée
- Système de recommandations
- Analytics et métriques détaillées
- Optimisation des performances


## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

**Développé avec ❤️ pour HS Traiteur**
