// Helper to get image URL from imageData or use placeholder
export const getImageUrl = (imageData: string | null | undefined): string => {
  if (imageData) {
    return imageData;
  }
  return 'https://via.placeholder.com/300x200?text=No+Image';
};
