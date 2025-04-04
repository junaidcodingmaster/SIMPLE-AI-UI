# Server Configuration Documentation

## Configuration File: `config.env`

This file contains environment variables that configure the server and application behavior. Below are the available configuration options:

### 1. Server Configuration

- **`SIMPLE_AI_UI_SERVER_HOST`**
  - **Description**: The host address on which the server will listen for incoming requests.
  - **Default Value**: `localhost` (listens on all available interfaces)
  - **Example**: 
    ```env
    SIMPLE_AI_UI_SERVER_HOST=localhost
    ```

- **`SIMPLE_AI_UI_SERVER_PORT`**
  - **Description**: The port number on which the server will listen for incoming requests.
  - **Default Value**: `5000`
  - **Example**: 
    ```env
    SIMPLE_AI_UI_SERVER_PORT=5000
    ```

### 2. User Configuration

- **`SIMPLE_AI_UI_AUTH_USERS`**
  - **Description**: A list of authorized users in the format `username:password`. This is used for user authentication.
  - **Example**: 
    ```env
    SIMPLE_AI_UI_AUTH_USERS=joe:1234
    ```

- **`SIMPLE_AI_UI_AUTH_NO_OF_USERS_PER_DAY`**
  - **Description**: The maximum number of users that can authenticate per day.
  - **Default Value**: `1000`
  - **Example**: 
    ```env
    SIMPLE_AI_UI_AUTH_NO_OF_USERS_PER_DAY=1000
    ```

- **`SIMPLE_AI_UI_AUTH_SHOW_USER_STATS`**
  - **Description**: A boolean value that determines whether to show user statistics.
  - **Default Value**: `true`
  - **Example**: 
    ```env
    SIMPLE_AI_UI_AUTH_SHOW_USER_STATS=true
    ```

### 3. API Request Configuration

- **`SIMPLE_AI_UI_API_LIMIT_OF_REQS_PER_DAY`**
  - **Description**: The maximum number of API requests allowed per day.
  - **Default Value**: `1000`
  - **Example**: 
    ```env
    SIMPLE_AI_UI_API_LIMIT_OF_REQS_PER_DAY=1000
    ```

- **`SIMPLE_AI_UI_API_NO_OF_DEVICES`**
  - **Description**: The maximum number of devices that can make API requests.
  - **Default Value**: `1000`
  - **Example**: 
    ```env
    SIMPLE_AI_UI_API_NO_OF_DEVICES=1000
    ```

---

### Usage

To use these configurations, create a file named `config.env` in your project directory and populate it with the desired settings. The application will read these environment variables at startup to configure its behavior accordingly.

### Example `config.env` File

```env
# Server Configuration
SIMPLE_AI_UI_SERVER_HOST=localhost
SIMPLE_AI_UI_SERVER_PORT=5000                   

# User Configuration
SIMPLE_AI_UI_AUTH_USERS=joe:1234
SIMPLE_AI_UI_AUTH_NO_OF_USERS_PER_DAY=1000
SIMPLE_AI_UI_AUTH_SHOW_USER_STATS=true      

# API Request Configuration
SIMPLE_AI_UI_API_LIMIT_OF_REQS_PER_DAY=1000     
SIMPLE_AI_UI_API_NO_OF_DEVICES=1000             