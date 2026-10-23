"""
Focused unit tests for CyberShieldAI FastAPI lifespan and monitor lifecycle.
Tests run using mocks without initiating live packet capture.
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_path = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(backend_path))

import asyncio
import unittest
from unittest.mock import MagicMock, patch

from app.main import app, lifespan
from app.services.live_flow_monitor import LiveFlowMonitor, live_flow_monitor


class TestLifespanAndLifecycle(unittest.IsolatedAsyncioTestCase):

    async def test_01_successful_startup(self):
        """1. Verify successful startup starts monitor and verifies healthy state."""
        with patch.object(live_flow_monitor, "start") as mock_start, \
             patch.object(live_flow_monitor, "stop") as mock_stop, \
             patch.object(live_flow_monitor, "_sniffer_active", side_effect=[True, False]), \
             patch.object(live_flow_monitor, "status", return_value={"running": True, "last_error": None}):

            mock_start.return_value = {
                "status": "started",
                "interface": "Wi-Fi",
                "device": r"\Device\NPF_{MOCK}",
                "capture_mode": "passive"
            }
            mock_stop.return_value = {"status": "stop_requested"}

            entered = False
            async with lifespan(app):
                entered = True
                self.assertTrue(entered)
                mock_start.assert_called_once()

            mock_stop.assert_called_once()

    async def test_02_startup_failure(self):
        """2. Verify startup failure reports error and keeps server available without monitoring."""
        with patch.object(live_flow_monitor, "start") as mock_start, \
             patch.object(live_flow_monitor, "stop") as mock_stop, \
             patch.object(live_flow_monitor, "_sniffer_active", return_value=False), \
             patch.object(live_flow_monitor, "status", return_value={"running": False, "last_error": "No interfaces found"}):

            mock_start.return_value = {
                "status": "error",
                "error": "No interfaces found",
                "capture_mode": "passive"
            }
            mock_stop.return_value = {"status": "stop_requested"}

            entered = False
            async with lifespan(app):
                entered = True

            self.assertTrue(entered, "FastAPI server must remain available even if capture fails to start")
            mock_start.assert_called_once()
            mock_stop.assert_called_once()

    async def test_03_repeated_startup_without_duplicate_sniffers(self):
        """3. Verify repeated startup does not create duplicate capture sessions."""
        monitor = LiveFlowMonitor()
        mock_sniffer = MagicMock()
        mock_sniffer.running = True
        mock_sniffer._thread = MagicMock()
        mock_sniffer._thread.is_alive.return_value = True

        monitor._sniffer = mock_sniffer
        monitor._running = True

        # Second start call while sniffer active
        result = monitor.start()
        self.assertEqual(result["status"], "error")
        self.assertIn("previous capture still running", result["error"])

    async def test_04_shutdown_after_successful_startup(self):
        """4. Verify shutdown after successful startup calls stop and clears sniffer."""
        monitor = LiveFlowMonitor()
        mock_sniffer = MagicMock()
        mock_sniffer.running = True
        mock_sniffer._thread = MagicMock()
        mock_sniffer._thread.is_alive.return_value = True

        def fake_stop():
            mock_sniffer.running = False
            mock_sniffer._thread.is_alive.return_value = False

        mock_sniffer.stop.side_effect = fake_stop
        monitor._sniffer = mock_sniffer
        monitor._running = True

        result = monitor.stop()
        self.assertEqual(result["status"], "stop_requested")
        self.assertFalse(monitor._sniffer_active())
        self.assertIsNone(monitor._sniffer)

    async def test_05_shutdown_when_capture_thread_fails_to_terminate(self):
        """5. Verify shutdown when thread remains alive retains reference and reports incomplete shutdown."""
        monitor = LiveFlowMonitor()
        stubborn_sniffer = MagicMock()
        stubborn_sniffer.running = True
        stubborn_sniffer._thread = MagicMock()
        stubborn_sniffer._thread.is_alive.return_value = True  # Never terminates

        monitor._sniffer = stubborn_sniffer
        monitor._running = True

        # Call stop
        result = monitor.stop()
        self.assertEqual(result["status"], "stop_requested")
        # Because thread is still alive, sniffer reference must NOT be cleared
        self.assertIsNotNone(monitor._sniffer)
        self.assertTrue(monitor._sniffer_active())

    async def test_06_subsequent_startup_when_previous_capture_still_active(self):
        """6. Verify subsequent startup is rejected if prior sniffer or thread remains active."""
        monitor = LiveFlowMonitor()
        stubborn_sniffer = MagicMock()
        stubborn_sniffer.running = False
        stubborn_sniffer._thread = MagicMock()
        stubborn_sniffer._thread.is_alive.return_value = True  # Thread still running

        monitor._sniffer = stubborn_sniffer
        monitor._running = False

        res = monitor.start()
        self.assertEqual(res["status"], "error")
        self.assertIn("previous capture still running", res["error"])

    async def test_07_cleanup_when_lifespan_exits_due_to_exception(self):
        """7. Verify cleanup is executed when lifespan exits due to an unhandled exception."""
        with patch.object(live_flow_monitor, "start") as mock_start, \
             patch.object(live_flow_monitor, "stop") as mock_stop, \
             patch.object(live_flow_monitor, "_sniffer_active", side_effect=[True, False]), \
             patch.object(live_flow_monitor, "status", return_value={"running": True, "last_error": None}):

            mock_start.return_value = {
                "status": "started",
                "interface": "Wi-Fi",
                "device": r"\Device\NPF_{MOCK}",
                "capture_mode": "passive"
            }
            mock_stop.return_value = {"status": "stop_requested"}

            with self.assertRaises(RuntimeError):
                async with lifespan(app):
                    raise RuntimeError("Simulated runtime application crash")

            # stop must have been invoked in finally block
            mock_stop.assert_called_once()

    async def test_08_already_running_accepted_if_healthy(self):
        """8. Verify already_running is accepted if verified healthy."""
        with patch.object(live_flow_monitor, "start") as mock_start, \
             patch.object(live_flow_monitor, "stop") as mock_stop, \
             patch.object(live_flow_monitor, "_sniffer_active", side_effect=[True, False]), \
             patch.object(live_flow_monitor, "status", return_value={"running": True, "last_error": None}):

            mock_start.return_value = {
                "status": "already_running",
                "interface": "Wi-Fi",
                "capture_mode": "passive"
            }
            mock_stop.return_value = {"status": "stop_requested"}

            entered = False
            async with lifespan(app):
                entered = True

            self.assertTrue(entered)
            mock_start.assert_called_once()
            mock_stop.assert_called_once()

    async def test_09_already_running_rejected_if_unhealthy(self):
        """9. Verify already_running is rejected if sniffer is inactive or status has errors."""
        with patch.object(live_flow_monitor, "start") as mock_start, \
             patch.object(live_flow_monitor, "stop") as mock_stop, \
             patch.object(live_flow_monitor, "_sniffer_active", return_value=False), \
             patch.object(live_flow_monitor, "status", return_value={"running": True, "last_error": "SnifferError"}):

            mock_start.return_value = {
                "status": "already_running",
                "interface": "Wi-Fi",
                "capture_mode": "passive"
            }
            mock_stop.return_value = {"status": "stop_requested"}

            entered = False
            async with lifespan(app):
                entered = True

            # Server remains online per policy, but error logged
            self.assertTrue(entered)
            mock_start.assert_called_once()
            mock_stop.assert_called_once()

    async def test_10_started_but_health_check_fails(self):
        """10. If start() returns started but capture-health check fails, update monitor state and stop cleanly."""
        with patch.object(live_flow_monitor, "start") as mock_start, \
             patch.object(live_flow_monitor, "stop") as mock_stop, \
             patch.object(live_flow_monitor, "_sniffer_active", return_value=False):

            mock_start.return_value = {
                "status": "started",
                "interface": "Wi-Fi",
                "device": r"\Device\NPF_{MOCK}",
                "capture_mode": "passive"
            }
            mock_stop.return_value = {"status": "stop_requested"}

            # Set monitor._running to True as start() would do
            live_flow_monitor._running = True
            live_flow_monitor._last_error = None

            entered = False
            async with lifespan(app):
                entered = True
                # Inside lifespan, monitor running should have been marked False due to health check failure
                self.assertFalse(live_flow_monitor._running)
                self.assertIn("StartupHealthCheckFailed", live_flow_monitor._last_error)

            self.assertTrue(entered)
            mock_start.assert_called_once()
            # stop should have been called for cleanup
            self.assertTrue(mock_stop.called)

    async def test_11_start_partial_initialization_exception_cleanup(self):
        """11. If candidate_sniffer.start() raises, cleanup is attempted and original error preserved."""
        monitor = LiveFlowMonitor()
        mock_sniffer = MagicMock()
        mock_sniffer.start.side_effect = RuntimeError("Socket creation failed")
        mock_sniffer.running = False
        mock_sniffer._thread = MagicMock()
        mock_sniffer._thread.is_alive.return_value = False

        with patch("app.services.live_flow_monitor.AsyncSniffer", return_value=mock_sniffer), \
             patch("app.services.live_flow_monitor.resolve_capture_interface", return_value=("dev", "Wi-Fi")):
            result = monitor.start()
            self.assertEqual(result["status"], "error")
            self.assertIn("Socket creation failed", result["error"])
            # Verify cleanup was attempted on the sniffer
            mock_sniffer.stop.assert_called_once()
            self.assertFalse(monitor._running)
            self.assertIn("Socket creation failed", monitor._last_error)


if __name__ == "__main__":
    unittest.main()
