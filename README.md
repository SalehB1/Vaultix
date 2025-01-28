# Vaultix IAM Service

A modern Identity and Access Management (IAM) service built with FastAPI, featuring custom implementations and enterprise-grade authentication flows.

## ✨ Core Features

### Custom FastAPI Extensions
- 🔧 Class-based views (CBV) implementation
- 🛣️ Enhanced router with trailing slash support
- 🔄 Custom middleware system

### Authentication Methods
- 📧 Email/Password authentication
- 📱 Phone number with OTP
- ✨ Magic link authentication
- 🔑 OAuth2 providers:
  - Google
  - GitHub
- 🎟️ JWT with refresh tokens

### User Management
- 👤 Profile management
- ✉️ Email verification
- 📞 Phone verification
- 🔐 Password reset/recovery
- 🖼️ Profile picture support

### Security Features
- 🔒 Role-based access control (RBAC)
- 🛡️ Custom permissions system 
- 🍪 Secure cookie management
- 🚦 Rate limiting
- 🌐 CORS protection

## 🛠️ Tech Stack

- FastAPI
- PostgreSQL
- Redis
- Docker
- Nginx
- Alembic
- SQLAlchemy

## 📦 Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/vaultix-iam.git
cd vaultix-iam
```

2. Configure environment variables
```bash
cp .env.example .env
# Edit .env with your configurations
```

3. Run with Docker
```bash
docker-compose up --build
```

## 🚀 Roadmap

### Phase 1: Authentication Enhancements
- [ ] WebAuthn/FIDO2 support
- [ ] Multi-factor authentication
- [ ] Hardware token support
- [ ] Additional OAuth providers

### Phase 2: Advanced Authorization
- [ ] Dynamic permission evaluation
- [ ] Resource-level permissions
- [ ] Organization/Team management
- [ ] API key management

### Phase 3: Security & Monitoring
- [ ] Advanced audit logging
- [ ] Brute force protection
- [ ] Session management
- [ ] Device fingerprinting
- [ ] Health monitoring system

### Phase 4: Enterprise Features
- [ ] Admin dashboard
- [ ] Webhook system
- [ ] Plugin architecture
- [ ] API versioning
- [ ] Multi-tenant support

## 📚 API Documentation

After starting the server, access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`


## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the AGPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## 💡 Custom Implementations

The project includes several custom implementations:
- Class-based views for FastAPI
- Enhanced router with uniform slash handling
- Custom middleware system
- Advanced authentication flows
- Service layer architecture

## 🔜 Incoming Future Features

1. Authentication Enhancements
- Biometric authentication
- Certificate-based auth
- Single Sign-On (SSO)

2. Authorization
- Dynamic permission system
- Resource-level access control
- Role inheritance

3. Infrastructure
- Distributed caching
- Database optimization
- Performance monitoring

4. Integration
- Event system
- Webhook management
- Plugin system

## 📞 Support

For support, please open an issue in the GitHub repository.

---
Made with ❤️ by [Saleh]
