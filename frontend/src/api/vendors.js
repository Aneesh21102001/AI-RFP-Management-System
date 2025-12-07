import client from './client';

export const vendorsApi = {
  getAll: async () => {
    const response = await client.get('/vendors');
    return response.data;
  },

  getById: async (id) => {
    const response = await client.get(`/vendors/${id}`);
    return response.data;
  },

  create: async (vendor) => {
    const response = await client.post('/vendors', vendor);
    return response.data;
  },

  update: async (id, vendor) => {
    const response = await client.put(`/vendors/${id}`, vendor);
    return response.data;
  },

  delete: async (id) => {
    await client.delete(`/vendors/${id}`);
  },
};
