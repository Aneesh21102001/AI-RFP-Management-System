import client from './client';

export const rfpsApi = {
  getAll: async () => {
    const response = await client.get('/rfps');
    return response.data;
  },

  getById: async (id) => {
    const response = await client.get(`/rfps/${id}`);
    return response.data;
  },

  createFromText: async (text) => {
    const response = await client.post('/rfps/from-text', { text });
    return response.data;
  },

  create: async (rfp) => {
    const response = await client.post('/rfps', rfp);
    return response.data;
  },

  update: async (id, rfp) => {
    const response = await client.put(`/rfps/${id}`, rfp);
    return response.data;
  },

  delete: async (id) => {
    await client.delete(`/rfps/${id}`);
  },
};
