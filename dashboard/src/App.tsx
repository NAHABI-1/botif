import { Link } from "react-router-dom";

export default function App() {
  return (
    <div style={{ fontFamily: "system-ui", padding: 24 }}>
      <h1>MT5 Operator Dashboard</h1>
      <p>Dashboard shell is ready for integration.</p>
      <ul>
        <li>
          <Link to="/">Overview</Link>
        </li>
      </ul>
    </div>
  );
}
