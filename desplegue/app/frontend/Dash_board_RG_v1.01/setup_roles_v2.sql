INSERT INTO dw.roles (role_id, role_name, description)
VALUES 
    (3, 'GERENCIA', 'Acceso a métricas de alto nivel y KPIs estratégicos'),
    (4, 'MESA_AYUDA', 'Acceso a búsqueda de trámites y validación de proyectos'),
    (5, 'DESARROLLADOR', 'Acceso total a herramientas de depuración y analítica'),
    (6, 'QA', 'Acceso a validación de integridad y flujos de trabajo')
ON CONFLICT (role_id) DO UPDATE SET 
    role_name = EXCLUDED.role_name, 
    description = EXCLUDED.description;
