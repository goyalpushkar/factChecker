import type {NextConfig} from 'next';
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');

const nextConfig: NextConfig = {
  /* config options here */
  typescript: {
    ignoreBuildErrors: true,
  },
  // experimental: {
  //   // Enable turbopack for faster local development
  //   turbopack: false,
  // },
  eslint: {
    ignoreDuringBuilds: true,
  },
  /* This is added to avoid using server side modules from being included in the
   client-side bundle.
   Build process was giving error for modules like dns dgram that are node.js buil tin modules
   */
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        dns: false,
        dgram: false,
        fs: false,
        net: false,
        tls: false,
        pg: false, // Add this line to explicitly exclude pg
      };
      
      config.resolve.alias = {
        ...config.resolve.alias,
        pg: require.resolve('./mocks/pg.js'),
      };
      
      config.plugins.push(
        new BundleAnalyzerPlugin({
          analyzerMode: 'static',
          generateStatsFile: true,
          statsFilename: '../analyze/client.json', // Output path for the report
          reportTitle: 'client',
          openAnalyzer: false, // Set to true to open the report automatically
          reportFilename: '../analyze/client.html', // Output path for the report
        })
      );
    }
    else {
        config.plugins = config.plugins.filter(
          (plugin) => plugin.constructor.name !== 'BundleAnalyzerPlugin'
        );
        config.plugins.push(
          new BundleAnalyzerPlugin({
            analyzerMode: 'disabled',
          })
        );

      }

    return config;
  },
};

export default nextConfig;
