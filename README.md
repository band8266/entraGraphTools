# Entra Tools Library

A suite of automation tools for Microsoft Entra (Azure AD) and related platforms, designed to streamline identity, security, and access management workflows. This library includes scripts for extracting department data, processing DLP alerts, and synchronizing user profile photos with Verkada.

## Features

- **entraDepts.py**  
  Extracts unique department names from all enabled, active users in Microsoft Entra (Azure AD) using the Microsoft Graph API.

- **entraDLP2KB4.py**  
  Fetches Data Loss Prevention (DLP) alerts from Microsoft Graph Security API and forwards them to KnowBe4 for security event tracking and automation.

- **entraPic2Verkada.py**  
  Synchronizes user profile photos from Microsoft Entra to Verkada access control systems, ensuring user images are up-to-date across platforms.

 
## Requirements

- Python 3.8 or later
- msal
- python-dotenv
- requests


## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/entraGraphTools.git
   cd entraGraphTools
   ```

2. **Install dependencies**
   Ensure you have Python 3.8+ and pip installed. Then run:
   ```bash
   pip3 install msal python-dotenv requests
   ```

   If a `requirements.txt` file is provided, you can instead run:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Configure environment variables**
   Create a `.env` file in the project root with the following keys:
   ```
   TENANT_ID=your-tenant-id
   CLIENT_ID=your-client-id
   CLIENT_SECRET=your-client-secret
   KB4_EVENT_API_KEY=your-knowbe4-api-key
   GROUP_ID=your-entra-group-id
   VERKADA_API_KEY=your-verkada-api-key
   VERKADA_REGION=api  # or 'eu', 'ca', etc.
   ```
Optionally set `KB4_EVENT_URL` to override the default KnowBe4 endpoint.

## Usage

Each script loads configuration from the `.env` file. Run scripts with Python 3:

- **Extract departments**
  ```bash
  python3 entraDepts.py
  ```

- **Process DLP alerts and forward to KnowBe4**
  ```bash
  python3 entraDLP2KB4.py
  ```

- **Sync user photos to Verkada**
  ```bash
  python3 entraPic2Verkada.py
  ```

## Security

- Never commit your `.env` file or secrets to version control.
- Use least-privilege principles for all API keys and service accounts.

## Contributing

Pull requests and issues are welcome! Please open an issue to discuss major changes.

## License

[MIT License](LICENSE)
