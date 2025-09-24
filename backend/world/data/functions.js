// Comprehensive list of functions/areas of responsibility for business applications
export const functions = [
  {
    "name": "Administración",
    "code": "ADM",
    "relevanceScore": 5
  },
  {
    "name": "Asesor Financiero",
    "code": "IFA",
    "relevanceScore": 7
  },
  {
    "name": "Auditoria/Control",
    "code": "AUD",
    "relevanceScore": 6
  },
  {
    "name": "Broker/trader",
    "code": "RES",
    "relevanceScore": 4
  },
  {
    "name": "Compras/Abastecimiento",
    "code": "BUY",
    "relevanceScore": 7
  },
  {
    "name": "Comunicaciones/Relaciones Públicas",
    "code": "PRB",
    "relevanceScore": 7
  },
  {
    "name": "Contabilidad/Finanzas",
    "code": "FIN",
    "relevanceScore": 7
  },
  {
    "name": "Control de Calidad/Procesos",
    "code": "QUA",
    "relevanceScore": 7
  },
  {
    "name": "Cumplimiento/Gestión del Riesgo",
    "code": "RSK",
    "relevanceScore": 7
  },
  {
    "name": "Dinero/Gestión de Cartera",
    "code": "MON",
    "relevanceScore": 6
  },
  {
    "name": "Estrategia/Planeamiento",
    "code": "CPL",
    "relevanceScore": 9
  },
  {
    "name": "Estudiante",
    "code": "STU",
    "relevanceScore": 3
  },
  {
    "name": "Gerencia",
    "code": "CON",
    "relevanceScore": 9
  },
  {
    "name": "Gestión del Conocimiento",
    "code": "KNO",
    "relevanceScore": 5
  },
  {
    "name": "Gestión/Desarrollo de Productos",
    "code": "PRO",
    "relevanceScore": 7
  },
  {
    "name": "Inversionista Privado",
    "code": "PRI",
    "relevanceScore": 6
  },
  {
    "name": "Investigación/Análisis",
    "code": "RAD",
    "relevanceScore": 5
  },
  {
    "name": "Legal/Secretaría de la Empresa",
    "code": "LEG",
    "relevanceScore": 7
  },
  {
    "name": "Logística",
    "code": "LOG",
    "relevanceScore": 7
  },
  {
    "name": "Marketing",
    "code": "MKT",
    "relevanceScore": 9
  },
  {
    "name": "Operaciones",
    "code": "OPS",
    "relevanceScore": 9
  },
  {
    "name": "Responsabilidad Social",
    "code": "CSR",
    "relevanceScore": 5
  },
  {
    "name": "Retirado o Jubilado",
    "code": "RET",
    "relevanceScore": 3
  },
  {
    "name": "RRHH/Capacitación",
    "code": "PAT",
    "relevanceScore": 7
  },
  {
    "name": "Seguridad y Salud en el Trabajo",
    "code": "SST",
    "relevanceScore": 5
  },
  {
    "name": "Sostenibilidad",
    "code": "SOS",
    "relevanceScore": 5
  },
  {
    "name": "Tecnología de la Información",
    "code": "TEC",
    "relevanceScore": 9
  },
  {
    "name": "Ventas/Desarrollo de Negocios",
    "code": "SAL",
    "relevanceScore": 9
  }
];

// Helper functions for function data access
export const getFunctionByCode = (code) => {
  return functions.find(func => func.code === code);
};

export const getFunctionByName = (name) => {
  return functions.find(func => func.name === name);
};

export const getFunctionsSortedByName = () => {
  return [...functions].sort((a, b) => a.name.localeCompare(b.name));
};

export const getFunctionCodes = () => {
  return functions.map(func => func.code);
};

export const getFunctionNames = () => {
  return functions.map(func => func.name);
};

export const getFunctionRelevanceScore = (functionName) => {
  const func = functions.find(func => func.name === functionName);
  return func?.relevanceScore || 6; // Default to 6 if not found
};

export const getFunctionsByRelevance = (minScore = 0, maxScore = 10) => {
  return functions.filter(func => 
    func.relevanceScore >= minScore && func.relevanceScore <= maxScore
  );
};

export const getHighRelevanceFunctions = () => {
  return getFunctionsByRelevance(8, 10);
};

export const getMediumRelevanceFunctions = () => {
  return getFunctionsByRelevance(6, 7);
};

export const getLowRelevanceFunctions = () => {
  return getFunctionsByRelevance(3, 5);
};
