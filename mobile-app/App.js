import React, { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  Platform,
  StyleSheet,
  Text,
  View,
} from 'react-native';

// Update this to your local machine IPv4 when testing on a physical device.
const BASE_URL = Platform.select({
  android: 'http://192.168.1.5:8000',
  ios: 'http://127.0.0.1:8000',
  default: 'http://127.0.0.1:8000',
});

export default function App() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchReports = async () => {
    try {
      const response = await fetch(`${BASE_URL}/reports/latest?limit=10`);
      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const data = await response.json();
      setReports(data.reports || []);
      setError(null);
    } catch (err) {
      setError(err.message || 'Failed to load reports');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
    const intervalId = setInterval(fetchReports, 4000);
    return () => clearInterval(intervalId);
  }, []);

  const renderReport = ({ item }) => (
    <View style={styles.card}>
      <Text style={styles.reportId}>{item.report_id}</Text>
      <Text style={styles.status}>{item.status || 'Pending'}</Text>
      <Text style={styles.meta}>{item.severity || 'Unknown severity'}</Text>
      <Text style={styles.meta}>{item.location_extracted || 'Location pending'}</Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>CIRO Emergency Dashboard</Text>
      <Text style={styles.subtitle}>Polling from {BASE_URL}</Text>

      {loading && !reports.length ? (
        <ActivityIndicator size="large" color="#2563eb" />
      ) : null}

      {error ? <Text style={styles.errorText}>{error}</Text> : null}

      <FlatList
        data={reports}
        keyExtractor={(item) => item.report_id}
        renderItem={renderReport}
        contentContainerStyle={styles.list}
        ListEmptyComponent={<Text style={styles.empty}>No reports yet.</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f3f4f6',
    paddingTop: 48,
    paddingHorizontal: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 13,
    color: '#6b7280',
    marginBottom: 16,
  },
  list: {
    paddingBottom: 24,
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 14,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  reportId: {
    fontSize: 15,
    fontWeight: '600',
    color: '#111827',
  },
  status: {
    marginTop: 4,
    color: '#2563eb',
    fontWeight: '600',
  },
  meta: {
    marginTop: 4,
    color: '#4b5563',
  },
  errorText: {
    color: '#dc2626',
    marginBottom: 12,
  },
  empty: {
    color: '#6b7280',
    textAlign: 'center',
    marginTop: 24,
  },
});
