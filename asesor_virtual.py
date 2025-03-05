# Mejoras al asesor virtual con lógica de suplementos
class AsesorNutricional:
    def generar_recomendacion(self, paciente, historial):
        recomendaciones = []
        # Lógica basada en perfil del paciente
        if not self._tiene_contraindicaciones(historial):
            if paciente.edad > 50:
                recomendaciones.append({"suplemento": "Omega3", "dosis": "1000mg", "motivo": "Salud cardiovascular"})
            
            if historial.deficit_vitaminico:
                recomendaciones.append({"suplemento": "Multivitamínico", "dosis": "1 tableta diaria", "motivo": "Déficit nutricional"})
        
        return {
            "recomendaciones": recomendaciones,
            "advertencias": self._generar_advertencias(historial)
        }

    def _tiene_contraindicaciones(self, historial):
        return any([
            historial.alergias.contains('pescado'),
            historial.medicamentos_actuales.contains('anticoagulantes'),
            historial.enfermedades_cronicas.contains('renal')
        ]) 