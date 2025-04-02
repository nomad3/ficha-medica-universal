import React, { useState } from 'react';
import axios from 'axios';

const SupplementHistoryForm = ({ pacienteId }) => {
  const [formData, setFormData] = useState({
    suplemento: 'Omega3',
    dosis: '1000mg',
    fecha_inicio: new Date().toISOString().split('T')[0],
    colesterol_total: 0,
    trigliceridos: 0,
    vitamina_d: 0,
    omega3_indice: 0,
    observaciones: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Crear objeto en formato FHIR MedicationStatement
      const medicationStatement = {
        resourceType: "MedicationStatement",
        status: "active",
        medicationCodeableConcept: {
          coding: [
            {
              system: "http://suplementos.cl/codigo",
              code: formData.suplemento,
              display: formData.suplemento
            }
          ],
          text: formData.suplemento
        },
        subject: {
          reference: `Patient/${pacienteId}`
        },
        effectivePeriod: {
          start: formData.fecha_inicio,
          end: null
        },
        dosage: [
          {
            text: formData.dosis
          }
        ],
        note: [
          {
            text: formData.observaciones
          }
        ]
      };

      // Crear observaciones FHIR para los valores bioquímicos
      const observations = [];
      
      if (formData.colesterol_total > 0) {
        observations.push({
          resourceType: "Observation",
          status: "final",
          code: {
            coding: [
              {
                system: "http://loinc.org",
                code: "2093-3",
                display: "Colesterol total"
              }
            ]
          },
          subject: {
            reference: `Patient/${pacienteId}`
          },
          effectiveDateTime: formData.fecha_inicio,
          valueQuantity: {
            value: parseInt(formData.colesterol_total),
            unit: "mg/dL",
            system: "http://unitsofmeasure.org",
            code: "mg/dL"
          }
        });
      }
      
      if (formData.trigliceridos > 0) {
        observations.push({
          resourceType: "Observation",
          status: "final",
          code: {
            coding: [
              {
                system: "http://loinc.org",
                code: "2571-8",
                display: "Triglicéridos"
              }
            ]
          },
          subject: {
            reference: `Patient/${pacienteId}`
          },
          effectiveDateTime: formData.fecha_inicio,
          valueQuantity: {
            value: parseInt(formData.trigliceridos),
            unit: "mg/dL",
            system: "http://unitsofmeasure.org",
            code: "mg/dL"
          }
        });
      }
      
      if (formData.vitamina_d > 0) {
        observations.push({
          resourceType: "Observation",
          status: "final",
          code: {
            coding: [
              {
                system: "http://loinc.org",
                code: "14635-7",
                display: "Vitamina D"
              }
            ]
          },
          subject: {
            reference: `Patient/${pacienteId}`
          },
          effectiveDateTime: formData.fecha_inicio,
          valueQuantity: {
            value: parseInt(formData.vitamina_d),
            unit: "ng/mL",
            system: "http://unitsofmeasure.org",
            code: "ng/mL"
          }
        });
      }
      
      if (formData.omega3_indice > 0) {
        observations.push({
          resourceType: "Observation",
          status: "final",
          code: {
            coding: [
              {
                system: "http://loinc.org",
                code: "omega3_indice",
                display: "Índice Omega-3"
              }
            ]
          },
          subject: {
            reference: `Patient/${pacienteId}`
          },
          effectiveDateTime: formData.fecha_inicio,
          valueQuantity: {
            value: parseInt(formData.omega3_indice),
            unit: "%",
            system: "http://unitsofmeasure.org",
            code: "%"
          }
        });
      }

      // Crear bundle FHIR con todos los recursos
      const bundle = {
        resourceType: "Bundle",
        type: "transaction",
        entry: [
          {
            resource: medicationStatement,
            request: {
              method: "POST",
              url: "MedicationStatement"
            }
          },
          ...observations.map(obs => ({
            resource: obs,
            request: {
              method: "POST",
              url: "Observation"
            }
          }))
        ]
      };

      // Enviar al servidor
      await axios.post('http://localhost:8000/fhir/import', bundle);
      
      // Limpiar formulario o mostrar mensaje de éxito
      alert('Registro de suplemento guardado correctamente');
      
      // Opcional: resetear formulario
      setFormData({
        suplemento: 'Omega3',
        dosis: '1000mg',
        fecha_inicio: new Date().toISOString().split('T')[0],
        colesterol_total: 0,
        trigliceridos: 0,
        vitamina_d: 0,
        omega3_indice: 0,
        observaciones: ''
      });
      
    } catch (error) {
      console.error('Error al guardar el registro:', error);
      alert('Error al guardar el registro');
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    // Wrap form in a card for consistent styling within the tab
    <div className="supplement-history-form card mb-3">
      <h4 className="mb-2">Nuevo Registro de Suplementación</h4>
      <form onSubmit={handleSubmit}>
        <div className="form-grid"> {/* Use grid for layout */}
          <div className="form-group">
            <label className="form-label" htmlFor="suplemento">Suplemento:</label>
            <select id="suplemento" name="suplemento" value={formData.suplemento} onChange={handleChange} className="form-select">
              <option value="Omega3">Omega 3</option>
              <option value="Multivitaminico">Multivitamínico</option>
              <option value="VitaminaD">Vitamina D</option>
              {/* Add more options as needed */}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="dosis">Dosis:</label>
            <input
              id="dosis"
              type="text"
              name="dosis"
              value={formData.dosis}
              onChange={handleChange}
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="fecha_inicio">Fecha de inicio:</label>
            <input
              id="fecha_inicio"
              type="date"
              name="fecha_inicio"
              value={formData.fecha_inicio}
              onChange={handleChange}
              className="form-input"
            />
          </div>
        </div>

        <h5 className="mt-2 mb-1 form-section-title">Valores Bioquímicos (Opcional)</h5>
        <div className="form-grid biomarker-grid"> {/* Grid for biomarkers */}
          <div className="form-group">
            <label className="form-label" htmlFor="colesterol_total">Colesterol (mg/dL):</label>
            <input
              id="colesterol_total"
              type="number"
              name="colesterol_total"
              value={formData.colesterol_total}
              onChange={handleChange}
              className="form-input"
              min="0"
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="trigliceridos">Triglicéridos (mg/dL):</label>
            <input
              id="trigliceridos"
              type="number"
              name="trigliceridos"
              value={formData.trigliceridos}
              onChange={handleChange}
              className="form-input"
              min="0"
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="vitamina_d">Vitamina D (ng/mL):</label>
            <input
              id="vitamina_d"
              type="number"
              name="vitamina_d"
              value={formData.vitamina_d}
              onChange={handleChange}
              className="form-input"
              min="0"
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="omega3_indice">Índice Omega-3 (%):</label>
            <input
              id="omega3_indice"
              type="number"
              name="omega3_indice"
              value={formData.omega3_indice}
              onChange={handleChange}
              className="form-input"
              min="0"
            />
          </div>
        </div>

        <div className="form-group mt-2">
          <label className="form-label" htmlFor="observaciones">Observaciones:</label>
          <textarea
            id="observaciones"
            name="observaciones"
            value={formData.observaciones}
            onChange={handleChange}
            className="form-textarea"
            rows="3"
          />
        </div>

        <button type="submit" className="form-button mt-2">Guardar Registro</button>
      </form>
    </div>
  );
};

export default SupplementHistoryForm;
