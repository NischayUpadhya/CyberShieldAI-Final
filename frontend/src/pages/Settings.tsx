export default function Settings() {
  return (
    <div className="space-y-6">
      
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-slate-400 mt-1">
          Configure CyberShield AI security and system preferences
        </p>
      </div>

      {/* General Settings */}
      <div className="bg-white rounded-2xl p-6 text-black">
        <h2 className="text-xl font-bold mb-6">General Settings</h2>

        <div className="space-y-5">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold">System Monitoring</h3>
              <p className="text-sm text-gray-500">
                Enable continuous security monitoring
              </p>
            </div>

            <div className="w-12 h-6 bg-cyan-500 rounded-full flex items-center justify-end px-1">
              <div className="w-4 h-4 bg-white rounded-full"></div>
            </div>
          </div>

          <div className="border-t pt-5">
            
            <label className="block font-semibold mb-2">
              Monitoring Interval
            </label>

            <select className="w-full border border-gray-300 rounded-lg p-3">
              <option>Real-time</option>
              <option>Every 30 seconds</option>
              <option>Every 1 minute</option>
              <option>Every 5 minutes</option>
            </select>
          </div>
        </div>
      </div>

      {/* Notification Settings */}
      <div className="bg-white rounded-2xl p-6 text-black">
        <h2 className="text-xl font-bold mb-6">Notification Settings</h2>

        <div className="space-y-5">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold">Critical Threat Alerts</h3>
              <p className="text-sm text-gray-500">
                Receive alerts when critical threats are detected
              </p>
            </div>

            <div className="w-12 h-6 bg-cyan-500 rounded-full flex items-center justify-end px-1">
              <div className="w-4 h-4 bg-white rounded-full"></div>
            </div>
          </div>

          <div className="border-t pt-5 flex items-center justify-between">
            <div>
              <h3 className="font-semibold">Blockchain Verification Alerts</h3>
              <p className="text-sm text-gray-500">
                Notify when blockchain records are verified
              </p>
            </div>

            <div className="w-12 h-6 bg-cyan-500 rounded-full flex items-center justify-end px-1">
              <div className="w-4 h-4 bg-white rounded-full"></div>
            </div>
          </div>
        </div>
      </div>

      {/* AI Detection Settings */}
      <div className="bg-white rounded-2xl p-6 text-black">
        <h2 className="text-xl font-bold mb-6">AI Detection Settings</h2>

        <div className="space-y-5">
          <div>
            <label className="block font-semibold mb-2">
              Detection Sensitivity
            </label>

            <select className="w-full border border-gray-300 rounded-lg p-3">
              <option>High</option>
              <option>Medium</option>
              <option>Low</option>
            </select>
          </div>

          <div className="border-t pt-5">
            <h3 className="font-semibold">Automatic Threat Response</h3>

            <p className="text-sm text-gray-500 mt-1 mb-3">
              Allow the AI system to automatically respond to detected threats
            </p>

            <div className="w-12 h-6 bg-cyan-500 rounded-full flex items-center justify-end px-1">
              <div className="w-4 h-4 bg-white rounded-full"></div>
            </div>
          </div>
        </div>
      </div>

      {/* Security Settings */}
      <div className="bg-white rounded-2xl p-6 text-black">
        <h2 className="text-xl font-bold mb-6">Security Settings</h2>

        <div className="space-y-5">
          <div>
            <h3 className="font-semibold">Threat Detection Mode</h3>

            <p className="text-sm text-gray-500 mt-1 mb-3">
              Current security mode
            </p>

            <span className="inline-block bg-green-100 text-green-700 px-4 py-2 rounded-lg font-semibold">
              Active
            </span>
          </div>

          <div className="border-t pt-5">
            <h3 className="font-semibold">Blockchain Integrity</h3>

            <p className="text-sm text-gray-500 mt-1">
              All security records are verified through the blockchain
              network.
            </p>

            <span className="inline-block mt-3 bg-green-100 text-green-700 px-4 py-2 rounded-lg font-semibold">
              Verified
            </span>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end pb-6">
        <button className="bg-cyan-500 hover:bg-cyan-600 text-white font-semibold px-6 py-3 rounded-lg">
          Save Settings
        </button>
      </div>

    </div>
  );
}