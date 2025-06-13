// eslint.config.mjs
import eslintPluginReact from 'eslint-plugin-react';

export default [
  {
    files: ['**/*.js', '**/*.jsx'],
    plugins: {
      react: eslintPluginReact,
    },
    languageOptions: {
      env: {
        jest: true, // ✅ Jest globals like test and expect
      },
      globals: {
        React: 'readonly',
      },
      parserOptions: {
        ecmaVersion: 2021,
        sourceType: 'module',
        ecmaFeatures: {
          jsx: true,
        },
      },
    },
    rules: {
      'react/react-in-jsx-scope': 'off', // Not needed in React 17+
      'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      'no-undef': 'error',
    },
    settings: {
      react: {
        version: 'detect',
      },
    },
    extends: [
      'eslint:recommended',
      'plugin:react/recommended',
    ],
  },
];
