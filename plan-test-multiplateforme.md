# Plan de test multi-plateforme — phenates-agents-plugins

## Phase 0 — Pré-requis

```bash
# Depuis Git Bash, à la racine du repo
git status
git log -1 --oneline

# Validation complète avant de commencer les tests plateforme
./scripts/validate.sh
# ou, si scripts npm en place :
npm run check
```

Noter l'état "avant" de chaque plateforme (captures ou liste) avant de commencer les tests ci-dessous.

---

## Phase 1 — Claude Code (CLI)

```bash
# Retirer l'ancienne marketplace si encore présente
/plugin marketplace remove phenates-skills

# Ajouter la nouvelle
/plugin marketplace add phenates/phenates-agents-plugins

# Installer le plugin
/plugin install phenates-agents-plugins@phenates-agents-plugins

# Vérifier ce qui est détecté
/plugin
# → Discover, confirmer les 5 skills avec les bonnes descriptions

# Validation stricte du manifeste natif
claude plugin validate --strict .
```

Test fonctionnel : demander à Claude Code d'éditer un fichier `.canvas` pour vérifier que la skill `json-canvas` se déclenche automatiquement.

---

## Phase 2 — npx skills (Vercel)

```bash
# Lister ce qui est détecté dans le repo
npx skills add https://github.com/phenates/phenates-agents-plugins -a claude-code -g --list

# Installer réellement
npx skills add https://github.com/phenates/phenates-agents-plugins -a claude-code -g

# Vérifier qu'il n'y a pas de résidu de l'ancien nom
ls ~/.claude/skills/
# (adapter le chemin selon l'environnement Windows / Git Bash, ex. $USERPROFILE/.claude/skills/)
```

---

## Phase 3 — Claude Desktop / Cowork

Pas de ligne de commande — via l'UI :

1. **Customize → Plugins → Personal plugins**
2. Retirer l'ancienne marketplace "Phenates skills"
3. **+ → Add marketplace → Add from a repository**
4. Coller : `https://github.com/phenates/phenates-agents-plugins`
5. Vérifier :
   - Badge "mis à jour il y a..."
   - Nombre de compétences = 5
   - Description reflète "plugin" et non "collection de skills"

Si le sync semble figé sur l'ancienne version : retirer puis ré-ajouter la marketplace (bug connu, pas de commande de contournement).

---

## Phase 4 — Hermes Agent

### 4a. Tap natif (méthode principale)

```bash
# Retirer l'ancien tap
hermes skills tap remove phenates/phenates-skills

# Ajouter le nouveau
hermes skills tap add phenates/phenates-agents-plugins

# Réinstaller chaque skill
hermes skills install phenates/phenates-agents-plugins/markdown-flavor
hermes skills install phenates/phenates-agents-plugins/obsidian-vault
hermes skills install phenates/phenates-agents-plugins/json-canvas
hermes skills install phenates/phenates-agents-plugins/obsidian-bases
hermes skills install phenates/phenates-agents-plugins/obsidian-cli

# Vérification
hermes skills check
```

### 4b. Chemin portable (test séparé, ne pas cumuler avec 4a sur les mêmes skills en simultané)

```bash
# Désactiver le tap natif le temps du test si besoin d'isoler
hermes skills tap remove phenates/phenates-agents-plugins

# Installer via le chemin portable Agent Plugins
hermes plugins install phenates/phenates-agents-plugins --no-enable
hermes plugins list
hermes plugins enable phenates-agents-plugins

# Vérification
hermes plugins doctor
```

Noter la différence de nommage observée : `markdown-flavor` (tap natif) vs `agent-plugin-markdown-flavor-<hash>` (portable).

---

## Phase 5 — Vérification croisée finale

```bash
# Ré-exécuter la validation complète après tous les tests, pour confirmer que rien n'a été cassé en route
./scripts/validate.sh
claude plugin validate --strict .
```

Comparer manuellement entre les 4 plateformes :
- [ ] Mêmes 5 skills visibles partout
- [ ] Mêmes descriptions
- [ ] Aucun résidu du nom `phenates-skills` en cache

---

## Phase 6 — Tableau de résultats à compléter

| Plateforme | Commande d'install | Statut | Version détectée | Notes / effets de bord |
|---|---|---|---|---|
| Claude Code (CLI) | `/plugin install phenates-agents-plugins@phenates-agents-plugins` | ☐ | | |
| npx skills (Vercel) | `npx skills add https://github.com/phenates/phenates-agents-plugins` | ☐ | | |
| Claude Desktop/Cowork | Add marketplace (UI) | ☐ | | |
| Hermes — tap natif | `hermes skills tap add phenates/phenates-agents-plugins` | ☐ | | |
| Hermes — portable | `hermes plugins install phenates/phenates-agents-plugins` | ☐ | | |

Une fois rempli, ce tableau alimente directement la section compatibilité du README.
