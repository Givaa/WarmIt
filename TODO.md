# WarmIt - TODO List

> **Note:** Per vedere le feature completate, consulta [CHANGELOG.md](CHANGELOG.md)

---

## 📋 TODO - Priorità Alta

### 🔔 Container Watchdog & Admin Notifications
- [ ] **Sistema notifiche admin**
  - Integrazione con Telegram/Discord/Email per notifiche
  - Alert automatici quando container va down
  - Alert per errori critici (rate limit, auth failures, etc.)
  - Dashboard status accessibile da remoto
  - Location: `src/warmit/services/health_monitor.py`, nuovo `src/warmit/services/notifications.py`

---

## 📋 TODO - Priorità Media

### 📈 Resource Optimization
- [ ] **Monitoraggio e ottimizzazione costi avanzato**
  - Dashboard costi API con grafici storici
  - Alert quando si superano soglie di spesa personalizzate
  - Statistiche costo per email inviata
  - Suggerimenti per ridurre costi (es. modelli più economici)
  - Export report costi
  - Location: Miglioramento di `dashboard/pages/api_costs.py`

### ⚙️ Configuration Management Avanzato
- [ ] **Auto-apply configuration profiles**
  - Applicazione automatica profili in base a numero accounts
  - CLI per cambiare profilo manualmente
  - Validazione configurazione prima dell'avvio
  - Hot-reload configurazione senza restart
  - Location: Miglioramento di `src/warmit/services/config_profiles.py`

---

## 📋 TODO - Priorità Bassa / Future

### 7. 📧 Email Template System
- [ ] Template personalizzabili per industry/use case
- [ ] A/B testing di subject lines e content
- [ ] Template marketplace/community

### 8. 📱 Mobile-Friendly Dashboard
- [ ] Responsive design per mobile
- [ ] Progressive Web App (PWA)
- [ ] Mobile app (React Native / Flutter)

### 9. 🌍 Internationalization
- [ ] Multi-language support (EN, IT, ES, FR, DE)
- [ ] Timezone auto-detection
- [ ] Locale-specific email templates

### 10. 📊 Advanced Analytics
- [ ] Machine learning per ottimizzare timing
- [ ] Predictive analytics per bounce rate
- [ ] Sentiment analysis delle risposte
- [ ] Heatmap engagement (giorni/orari migliori)

### 11. 🔌 Integrations
- [ ] Webhook support per eventi
- [ ] REST API completa per automazioni esterne
- [ ] Zapier/Make integration
- [ ] CRM integrations (HubSpot, Salesforce)

### 12. 🔒 Advanced Security
- [ ] Two-factor authentication (2FA)
- [ ] IP whitelist per dashboard
- [ ] Audit log completo
- [ ] Role-based access control (RBAC)
- [ ] SSO integration (OAuth, SAML)

### 13. 🚀 Performance & Scaling
- [ ] Horizontal scaling support
- [ ] Kubernetes deployment templates
- [ ] Load balancing tra multiple instances
- [ ] CDN integration per dashboard
- [ ] Database sharding per large deployments

---

## 🛠️ Technical Debt

- [ ] Aggiungere test unitari completi
- [ ] Aggiungere test di integrazione
- [ ] Documentazione API completa (OpenAPI)
- [ ] Logging strutturato (JSON logs)
- [ ] Metrics con Prometheus
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Dependency security scanning
- [ ] Code coverage report

---

## 📝 Note

### Come contribuire
1. Scegli una task dalla lista
2. Crea un issue su GitHub
3. Fai un fork e implementa
4. Apri una Pull Request

### Priorità dinamiche
Le priorità possono cambiare in base a:
- Feedback utenti
- Bug critici
- Nuove opportunità
- Dipendenze esterne

### Feature Requests
Apri un issue con label `feature-request` per suggerire nuove funzionalità.

---

**Ultima modifica**: 2026-01-15
**Versione WarmIt**: 0.2.0-dev

