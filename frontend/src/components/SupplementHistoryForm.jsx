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
    <form onSubmit={handleSubmit}>
      <h3>Registro de Suplementación</h3>
      <div>
        <label>Suplemento:</label>
        <select name="suplemento" value={formData.suplemento} onChange={handleChange}>
          <option value="Omega3">Omega 3</option>
          <option value="Multivitaminico">Multivitamínico</option>
          <option value="VitaminaD">Vitamina D</option>
        </select>
      </div>
      <div>
        <label>Dosis:</label>
        <input 
          type="text" 
          name="dosis" 
          value={formData.dosis} 
          onChange={handleChange} 
        />
      </div>
      <div>
        <label>Fecha de inicio:</label>
        <input 
          type="date" 
          name="fecha_inicio" 
          value={formData.fecha_inicio} 
          onChange={handleChange} 
        />
      </div>
      <div>
        <label>Colesterol total (mg/dL):</label>
        <input 
          type="number" 
          name="colesterol_total" 
          value={formData.colesterol_total} 
          onChange={handleChange} 
        />
      </div>
      <div>
        <label>Triglicéridos (mg/dL):</label>
        <input 
          type="number" 
          name="trigliceridos" 
          value={formData.trigliceridos} 
          onChange={handleChange} 
        />
      </div>
      <div>
        <label>Vitamina D (ng/mL):</label>
        <input 
          type="number" 
          name="vitamina_d" 
          value={formData.vitamina_d} 
          onChange={handleChange} 
        />
      </div>
      <div>
        <label>Índice Omega-3 (%):</label>
        <input 
          type="number" 
          name="omega3_indice" 
          value={formData.omega3_indice} 
          onChange={handleChange} 
        />
      </div>
      <div>
        <label>Observaciones:</label>
        <textarea 
          name="observaciones" 
          value={formData.observaciones} 
          onChange={handleChange} 
        />
      </div>
      <button type="submit">Guardar</button>
    </form>
  );
};

export default SupplementHistoryForm;
