// config-overrides.js
module.exports = function override(config, env) {
  // Modify Babel plugins here
  const babelLoader = config.module.rules.find(rule => rule.loader && rule.loader.includes('babel-loader'));
  if (babelLoader) {
    babelLoader.options.plugins = [
      "@babel/plugin-transform-private-methods",
      "@babel/plugin-transform-class-properties",
      "@babel/plugin-transform-numeric-separator",
      "@babel/plugin-transform-nullish-coalescing-operator",
      "@babel/plugin-transform-optional-chaining",
      ...babelLoader.options.plugins,
    ];
  }
  return config;
};
