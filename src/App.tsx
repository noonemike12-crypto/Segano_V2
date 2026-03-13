/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { motion } from "motion/react";
import { Download, Terminal, Shield, Lock, FileCode } from "lucide-react";

export default function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 font-sans selection:bg-indigo-500/30">
      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Header */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center justify-center p-3 bg-indigo-500/10 rounded-2xl mb-6 border border-indigo-500/20">
            <Shield className="w-12 h-12 text-indigo-400" />
          </div>
          <h1 className="text-5xl font-bold tracking-tight text-white mb-4">
            SIENG
          </h1>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto">
            Secure Incognito ENcryption Guard.
            A professional Python desktop suite for advanced steganography and encryption.
          </p>
        </motion.div>

        {/* Project Status */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="bg-slate-900/50 border border-slate-800 rounded-3xl p-8 mb-12 backdrop-blur-sm"
        >
          <div className="flex items-center gap-4 mb-6">
            <div className="w-3 h-3 bg-emerald-500 rounded-full animate-pulse" />
            <h2 className="text-lg font-semibold text-white">Project Ready for Download</h2>
          </div>
          
          <div className="grid md:grid-row-2 gap-6">
            <div className="space-y-4">
              <p className="text-slate-400">
                The full Python source code has been generated. This is a <strong>Desktop Application</strong> using PyQt5 and cannot run directly in the browser preview.
              </p>
              <div className="flex flex-wrap gap-3">
                <span className="px-3 py-1 bg-slate-800 rounded-full text-xs font-mono text-indigo-300 border border-slate-700">PyQt5 GUI</span>
                <span className="px-3 py-1 bg-slate-800 rounded-full text-xs font-mono text-indigo-300 border border-slate-700">AES/RSA/PGP</span>
                <span className="px-3 py-1 bg-slate-800 rounded-full text-xs font-mono text-indigo-300 border border-slate-700">Multi-Media Stego</span>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Instructions */}
        <div className="grid md:grid-cols-2 gap-8 mb-12">
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6"
          >
            <div className="flex items-center gap-3 mb-4 text-indigo-400">
              <Terminal className="w-5 h-5" />
              <h3 className="font-bold uppercase tracking-wider text-xs">Setup Instructions</h3>
            </div>
            <ol className="space-y-4 text-sm text-slate-400 list-decimal list-inside">
              <li>Open the <strong>Settings</strong> menu (top right) and select <strong>Export to ZIP</strong>.</li>
              <li>Extract the ZIP on your computer.</li>
              <li>Ensure you have <strong>Python 3.10+</strong> installed.</li>
              <li>Install dependencies: <br/>
                <code className="block mt-2 p-3 bg-black/40 rounded-lg text-indigo-300 border border-indigo-500/20">
                  pip install -r requirements.txt
                </code>
              </li>
              <li>Run the app: <br/>
                <code className="block mt-2 p-3 bg-black/40 rounded-lg text-indigo-300 border border-indigo-500/20">
                  python main.py
                </code>
              </li>
            </ol>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6"
          >
            <div className="flex items-center gap-3 mb-4 text-emerald-400">
              <Lock className="w-5 h-5" />
              <h3 className="font-bold uppercase tracking-wider text-xs">Security Features</h3>
            </div>
            <ul className="space-y-3 text-sm text-slate-400">
              <li className="flex items-start gap-2">
                <div className="mt-1.5 w-1.5 h-1.5 bg-emerald-500 rounded-full" />
                <span><strong>AES-256:</strong> Military-grade symmetric encryption.</span>
              </li>
              <li className="flex items-start gap-2">
                <div className="mt-1.5 w-1.5 h-1.5 bg-emerald-500 rounded-full" />
                <span><strong>RSA-2048:</strong> Secure asymmetric key exchange.</span>
              </li>
              <li className="flex items-start gap-2">
                <div className="mt-1.5 w-1.5 h-1.5 bg-emerald-500 rounded-full" />
                <span><strong>PGP:</strong> Digital signatures and identity verification.</span>
              </li>
              <li className="flex items-start gap-2">
                <div className="mt-1.5 w-1.5 h-1.5 bg-emerald-500 rounded-full" />
                <span><strong>Steganography:</strong> Hide data in Images, Audio, Video, and Metadata.</span>
              </li>
            </ul>
          </motion.div>
        </div>

        {/* Footer */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="text-center text-slate-500 text-xs border-t border-slate-800 pt-8"
        >
          <p>© 2024 SIENG Security Solutions. All rights reserved.</p>
          <p className="mt-2 italic">Built for privacy and secure communication.</p>
        </motion.div>
      </div>
    </div>
  );
}
