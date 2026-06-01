"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

type Prediction = {
  id: number;
  ticker: string;
  latest_close: number;
  predicted_next_close: number;
  trend: string;
  difference: number;
  percentage_change?: number;
  confidence?: number;
  created_at?: string;
};

type StockHistory = {
  date: string;
  close: number;
};

type Analytics = {
  total_predictions: number;
  bullish_predictions: number;
  bearish_predictions: number;
  most_predicted_stock: string;
};

export default function Home() {
  const [ticker, setTicker] = useState("AAPL");
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [history, setHistory] = useState<Prediction[]>([]);
  const [chartData, setChartData] = useState<StockHistory[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(false);

  const quickTickers = ["AAPL", "TSLA", "MSFT", "NVDA", "GOOG"];

  const fetchPrediction = async (selectedTicker = ticker) => {
    try {
      setLoading(true);

      const predictionResponse = await axios.get(
        `http://127.0.0.1:8000/predict/latest/${selectedTicker}`
      );

      const historyResponse = await axios.get(
        "http://127.0.0.1:8000/predictions/history"
      );

      const chartResponse = await axios.get(
        `http://127.0.0.1:8000/stock/history/${selectedTicker}`
      );

      const analyticsResponse = await axios.get(
        "http://127.0.0.1:8000/analytics/dashboard"
      );

      setPrediction(predictionResponse.data);
      setHistory(historyResponse.data);
      setChartData(chartResponse.data);
      setAnalytics(analyticsResponse.data);
    } catch (error) {
      console.error("API Error:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickTicker = (symbol: string) => {
    setTicker(symbol);
    fetchPrediction(symbol);
  };

  useEffect(() => {
    fetchPrediction("AAPL");
  }, []);

  const expectedReturn =
    prediction && prediction.latest_close
      ? ((prediction.difference / prediction.latest_close) * 100).toFixed(2)
      : "0.00";

  const riskLevel =
    prediction && Math.abs(Number(expectedReturn)) > 10
      ? "High"
      : prediction && Math.abs(Number(expectedReturn)) > 5
      ? "Medium"
      : "Low";

  return (
    <main className="min-h-screen bg-[#020617] text-white">
      <section className="mx-auto max-w-7xl px-6 py-10">
        <div className="mb-10 flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-5xl font-bold tracking-tight">FinSight AI</h1>
            <p className="mt-3 text-lg text-slate-400">
              AI-powered financial intelligence platform using LSTM, FastAPI,
              PostgreSQL, AWS S3 and Next.js.
            </p>
          </div>

          <div className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-5 py-3 text-sm text-emerald-400">
            Backend + Cloud Connected
          </div>
        </div>

        {analytics && (
          <div className="mb-8 grid gap-6 md:grid-cols-4">
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <p className="text-sm text-slate-400">Total Predictions</p>
              <h3 className="mt-3 text-3xl font-bold">
                {analytics.total_predictions}
              </h3>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <p className="text-sm text-slate-400">Bullish Signals</p>
              <h3 className="mt-3 text-3xl font-bold text-emerald-400">
                {analytics.bullish_predictions}
              </h3>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <p className="text-sm text-slate-400">Bearish Signals</p>
              <h3 className="mt-3 text-3xl font-bold text-red-400">
                {analytics.bearish_predictions}
              </h3>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <p className="text-sm text-slate-400">Most Tracked</p>
              <h3 className="mt-3 text-3xl font-bold">
                {analytics.most_predicted_stock}
              </h3>
            </div>
          </div>
        )}

        <div className="mb-8 rounded-2xl border border-slate-800 bg-slate-900/70 p-6 shadow-2xl">
          <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 className="text-2xl font-semibold">Stock Prediction</h2>
              <p className="text-slate-400">
                Enter a ticker symbol and generate next close prediction.
              </p>

              <div className="mt-5 flex flex-wrap gap-3">
                {quickTickers.map((symbol) => (
                  <button
                    key={symbol}
                    onClick={() => handleQuickTicker(symbol)}
                    className={`rounded-full border px-4 py-2 text-sm transition ${
                      ticker === symbol
                        ? "border-blue-500 bg-blue-500/20 text-blue-300"
                        : "border-slate-700 bg-slate-950 text-slate-300 hover:border-blue-500"
                    }`}
                  >
                    {symbol}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex gap-3">
              <input
                value={ticker}
                onChange={(e) => setTicker(e.target.value.toUpperCase())}
                className="w-36 rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none focus:border-blue-500"
                placeholder="AAPL"
              />

              <button
                onClick={() => fetchPrediction()}
                disabled={loading}
                className="rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white transition hover:bg-blue-700 disabled:opacity-60"
              >
                {loading ? "Predicting..." : "Predict"}
              </button>
            </div>
          </div>
        </div>

        {prediction && (
          <div className="mb-8 grid gap-6 md:grid-cols-4">
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <p className="text-sm text-slate-400">Ticker</p>
              <h3 className="mt-3 text-3xl font-bold">{prediction.ticker}</h3>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <p className="text-sm text-slate-400">Latest Close</p>
              <h3 className="mt-3 text-3xl font-bold">
                ${prediction.latest_close}
              </h3>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <p className="text-sm text-slate-400">AI Prediction</p>
              <h3 className="mt-3 text-3xl font-bold">
                ${prediction.predicted_next_close}
              </h3>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <p className="text-sm text-slate-400">Trend</p>
              <h3
                className={`mt-3 text-3xl font-bold ${
                  prediction.trend === "Bullish"
                    ? "text-emerald-400"
                    : "text-red-400"
                }`}
              >
                {prediction.trend}
              </h3>
            </div>
          </div>
        )}

        {prediction && (
          <div className="mb-8 grid gap-6 lg:grid-cols-3">
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 lg:col-span-2">
              <div className="mb-5 flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold">
                    Historical Price Chart
                  </h2>
                  <p className="text-sm text-slate-400">
                    6-month closing price movement for {prediction.ticker}
                  </p>
                </div>

                <span className="rounded-full bg-blue-500/10 px-3 py-1 text-sm text-blue-300">
                  Yahoo Finance
                </span>
              </div>

              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis
                      dataKey="date"
                      stroke="#94a3b8"
                      tick={{ fontSize: 12 }}
                    />
                    <YAxis stroke="#94a3b8" tick={{ fontSize: 12 }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#020617",
                        border: "1px solid #334155",
                        borderRadius: "12px",
                        color: "#fff",
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="close"
                      stroke="#38bdf8"
                      strokeWidth={3}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="mb-5 text-xl font-semibold">AI Confidence</h2>

              <p className="text-5xl font-bold text-emerald-400">
                {prediction.confidence ?? 0}%
              </p>

              <div className="mt-5 h-3 rounded-full bg-slate-800">
                <div
                  className="h-3 rounded-full bg-emerald-400"
                  style={{ width: `${prediction.confidence ?? 0}%` }}
                />
              </div>

              <div className="mt-8 space-y-5">
                <div>
                  <p className="text-sm text-slate-400">Expected Return</p>
                  <p
                    className={`text-2xl font-bold ${
                      Number(expectedReturn) >= 0
                        ? "text-emerald-400"
                        : "text-red-400"
                    }`}
                  >
                    {expectedReturn}%
                  </p>
                </div>

                <div>
                  <p className="text-sm text-slate-400">Risk Level</p>
                  <p
                    className={`text-2xl font-bold ${
                      riskLevel === "High"
                        ? "text-red-400"
                        : riskLevel === "Medium"
                        ? "text-yellow-400"
                        : "text-emerald-400"
                    }`}
                  >
                    {riskLevel}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <div className="mb-5 flex items-center justify-between">
            <h2 className="text-xl font-semibold">Prediction History</h2>
            <span className="text-sm text-slate-400">Latest 20 records</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="py-3">Ticker</th>
                  <th>Latest Close</th>
                  <th>Predicted</th>
                  <th>Trend</th>
                  <th>Difference</th>
                  <th>Time</th>
                </tr>
              </thead>

              <tbody>
                {history.map((item) => (
                  <tr
                    key={item.id}
                    className="border-b border-slate-800 text-slate-300"
                  >
                    <td className="py-4 font-semibold text-white">
                      {item.ticker}
                    </td>
                    <td>${item.latest_close}</td>
                    <td>${item.predicted_next_close}</td>
                    <td
                      className={
                        item.trend === "Bullish"
                          ? "text-emerald-400"
                          : "text-red-400"
                      }
                    >
                      {item.trend}
                    </td>
                    <td>{item.difference}</td>
                    <td>
                      {item.created_at
                        ? new Date(item.created_at).toLocaleString()
                        : "N/A"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </main>
  );
}