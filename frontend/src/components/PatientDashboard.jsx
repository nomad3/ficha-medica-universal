import React from 'react';
import GridLayout from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

// Placeholder layout for Patient Dashboard
const layout = [
  { i: 'wearable-data', x: 0, y: 0, w: 6, h: 4 },
  { i: 'appointments', x: 6, y: 0, w: 6, h: 4 },
  { i: 'medications', x: 0, y: 4, w: 12, h: 3 },
];

function PatientDashboard() {
  // TODO: Fetch and display actual patient data
  // TODO: Implement wearable data visualization
  // TODO: Implement appointment scheduling/viewing
  // TODO: Implement medication tracking

  return (
    // Adjust rowHeight and width as needed, or make width responsive
    <GridLayout className="dashboard-grid-layout" layout={layout} cols={12} rowHeight={50} width={1120} isDraggable={true} isResizable={true}>
      {/* Apply card class to each grid item */}
      <div key="wearable-data" className="card dashboard-widget">
        <h5 className="widget-title mb-1">Wearable Data</h5>
        {/* Placeholder for wearable data charts/widgets */}
        <div className="chart-placeholder mb-1">Chart: Heart Rate Trend</div>
        <p>Steps Today: ...</p>
        <p>Sleep Quality: ...</p>
      </div>
      <div key="appointments" className="card dashboard-widget">
        <h5 className="widget-title mb-1">Upcoming Appointments</h5>
        {/* Placeholder for appointment list */}
        <ul className="widget-list">
          <li>Dr. Smith - April 5th, 10:00 AM</li>
          <li>Dr. Jones - April 12th, 2:30 PM</li>
        </ul>
      </div>
      <div key="medications" className="card dashboard-widget">
        <h5 className="widget-title mb-1">Current Medications</h5>
        {/* Placeholder for medication list */}
        <ul className="widget-list">
          <li>Medication A - 10mg, daily</li>
          <li>Medication B - 50mg, twice daily</li>
        </ul>
      </div>
    </GridLayout>
  );
}

export default PatientDashboard;
