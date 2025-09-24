// Comprehensive list of positions for business applications
export const positions = [
  {
    "name": "Académico/Catedrático",
    "code": "AC",
    "authorityScore": 5
  },
  {
    "name": "Alta Gerencia (CFO/COO/CIO/CMO)",
    "code": "AG",
    "authorityScore": 9
  },
  {
    "name": "Analista",
    "code": "AN",
    "authorityScore": 5
  },
  {
    "name": "Asistente",
    "code": "AS",
    "authorityScore": 4
  },
  {
    "name": "CEO/Gerente General/Presidente de Directorio",
    "code": "CP",
    "authorityScore": 10
  },
  {
    "name": "Consultor",
    "code": "CT",
    "authorityScore": 7
  },
  {
    "name": "Coordinador Senior/Jefe de Departamento",
    "code": "JD",
    "authorityScore": 8
  },
  {
    "name": "Coordinador/Supervisor",
    "code": "CS",
    "authorityScore": 6
  },
  {
    "name": "Dueño/Socio/Propietario",
    "code": "DP",
    "authorityScore": 10
  },
  {
    "name": "Especialista de Negocio/Técnico",
    "code": "ET",
    "authorityScore": 6
  },
  {
    "name": "Estudiante de Posgrado",
    "code": "PG",
    "authorityScore": 4
  },
  {
    "name": "Estudiante de Pregrado",
    "code": "UG",
    "authorityScore": 3
  },
  {
    "name": "Gerencia Ejecutiva (EVP/SVP/MD)",
    "code": "GE",
    "authorityScore": 9
  },
  {
    "name": "Gerente o Jefe de Proyecto",
    "code": "PM",
    "authorityScore": 8
  },
  {
    "name": "Médico / Doctor",
    "code": "MD",
    "authorityScore": 6
  },
  {
    "name": "Otra",
    "code": "OT",
    "authorityScore": 5
  },
  {
    "name": "Profesional o Independiente",
    "code": "PR",
    "authorityScore": 6
  },
  {
    "name": "Secretario/Tesorero",
    "code": "ST",
    "authorityScore": 7
  },
  {
    "name": "Trainee/Practicante/Pasante",
    "code": "TR",
    "authorityScore": 3
  },
  {
    "name": "Vicepresidente/Director",
    "code": "VD",
    "authorityScore": 9
  }
];

// Helper functions for position data access
export const getPositionByCode = (code) => {
  return positions.find(position => position.code === code);
};

export const getPositionByName = (name) => {
  return positions.find(position => position.name === name);
};

export const getPositionsSortedByName = () => {
  return [...positions].sort((a, b) => a.name.localeCompare(b.name));
};

export const getPositionCodes = () => {
  return positions.map(position => position.code);
};

export const getPositionNames = () => {
  return positions.map(position => position.name);
};

export const getPositionAuthorityScore = (positionName) => {
  const position = positions.find(position => position.name === positionName);
  return position?.authorityScore || 5; // Default to 5 if not found
};

export const getPositionsByAuthority = (minScore = 0, maxScore = 10) => {
  return positions.filter(position => 
    position.authorityScore >= minScore && position.authorityScore <= maxScore
  );
};

export const getExecutivePositions = () => {
  return getPositionsByAuthority(9, 10);
};

export const getManagementPositions = () => {
  return getPositionsByAuthority(7, 8);
};

export const getOperationalPositions = () => {
  return getPositionsByAuthority(3, 6);
};
