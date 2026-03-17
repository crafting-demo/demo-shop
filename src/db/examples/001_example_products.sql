-- Example Products
-- Description: Inserts example products into the inventory if they don't already exist
-- Note: This script is idempotent and can be run multiple times safely

-- =============================================================================
-- Example Products for Demo Shop
-- =============================================================================

-- Placeholder Images (100x100 colored squares in PNG format)
-- These are small base64-encoded PNG images for demonstration purposes

-- Electronics (Blue #3B82F6)
INSERT INTO products (id, name, description, image_data, price_per_unit, count_in_stock, state, is_deleted)
VALUES
    ('11111111-1111-1111-1111-111111111111',
     'Wireless Bluetooth Headphones',
     'Premium noise-canceling wireless headphones with 30-hour battery life. Features active noise cancellation, ambient sound mode, and premium audio quality.',
     decode('iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAAp0lEQVR42u3RQREAMAjAsDFbczfRfMEGx6USmng/62hM1wIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgQAREQIAICBAB2V4DEvsDesH+f0kAAAAASUVORK5CYII=', 'base64'),
     14999, -- $149.99
     45,
     1, -- AVAILABLE
     false),

    ('22222222-2222-2222-2222-222222222222',
     'Gold Mesh Band Watch',
     'Elegant minimalist watch with gold-tone case and fine mesh bracelet band. Clean dial with slim profile. Japanese quartz movement. Water resistant.',
     decode('iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAAp0lEQVR42u3RQREAMAjAsDFbczfRfMEGx6USmng/62hM1wIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgQAREQIAICBAB2V4DEvsDesH+f0kAAAAASUVORK5CYII=', 'base64'),
     29999, -- $299.99
     32,
     1, -- AVAILABLE
     false),

    ('33333333-3333-3333-3333-333333333333',
     'Portable Wireless Speaker',
     'Waterproof Bluetooth speaker with 360-degree sound. Perfect for outdoor adventures with 12-hour battery life and rugged design.',
     decode('iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAAp0lEQVR42u3RQREAMAjAsDFbczfRfMEGx6USmng/62hM1wIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgQAREQIAICBAB2V4DEvsDesH+f0kAAAAASUVORK5CYII=', 'base64'),
     7999, -- $79.99
     67,
     1, -- AVAILABLE
     false),

    ('44444444-4444-4444-4444-444444444444',
     '4K Webcam',
     'Professional 4K webcam with auto-focus and dual microphones. Perfect for video conferencing, streaming, and content creation.',
     decode('iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAAp0lEQVR42u3RQREAMAjAsDFbczfRfMEGx6USmng/62hM1wIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgQAREQIAICBAB2V4DEvsDesH+f0kAAAAASUVORK5CYII=', 'base64'),
     12999, -- $129.99
     28,
     1, -- AVAILABLE
     false),

-- Home & Office (Brown #92400E)
    ('55555555-5555-5555-5555-555555555555',
     'Ergonomic Office Chair',
     'Premium ergonomic office chair with lumbar support, adjustable armrests, and breathable mesh back. Designed for all-day comfort.',
     decode('iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAAp0lEQVR42u3RAQ0AMAjAsHMB13SNGAYbhHQS1sj/6mhM1wIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgQAREQIAICBAB2V4D8xYCp60Ck18AAAAASUVORK5CYII=', 'base64'),
     34999, -- $349.99
     15,
     1, -- AVAILABLE
     false),

    ('66666666-6666-6666-6666-666666666666',
     'Hammered Metal Votive Holder',
     'Decorative hammered metal votive candle holder with faceted texture and brushed silver finish. Creates beautiful ambient lighting. Suitable for tea lights and small pillar candles.',
     decode('iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAAp0lEQVR42u3RAQ0AMAjAsHMB13SNGAYbhHQS1sj/6mhM1wIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgAgJEQIAICBABASIgQAREQIAICBAB2V4D8xYCp60Ck18AAAAASUVORK5CYII=', 'base64'),
     4999, -- $49.99
     89,
     1, -- AVAILABLE
     false),

    ('77777777-7777-7777-7777-777777777777',
     'Mechanical Keyboard',
     'RGB backlit mechanical keyboard with premium switches. Features customizable lighting, programmable keys, and durable construction.',
     decode('iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAABmJLR0QA/wD/AP+gvaeTAAAAVklEQVR4nO3BMQEAAADCoPVPbQwfoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOBnAJQAAAEgTii4AAAAAElFTkSuQmCC', 'base64'),
     8999, -- $89.99
     41,
     1, -- AVAILABLE
     false),

-- Books & Media (Orange #EA580C)
    ('88888888-8888-8888-8888-888888888888',
     'The Art of Programming',
     'Comprehensive guide to modern software development practices. Covers design patterns, clean code principles, and best practices.',
     decode('iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAABmJLR0QA/wD/AP+gvaeTAAAAVklEQVR4nO3BMQEAAADCoPVPbQwfoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOBnAOoAAAHd6FmfAAAAAElFTkSuQmCC', 'base64'),
     4599, -- $45.99
     125,
     1, -- AVAILABLE
     false),

    ('99999999-9999-9999-9999-999999999999',
     'Wireless Earbuds Pro',
     'True wireless earbuds with active noise cancellation and transparency mode. Features premium sound quality and 24-hour battery life with charging case.',
     decode('iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAABmJLR0QA/wD/AP+gvaeTAAAAVklEQVR4nO3BMQEAAADCoPVPbQwfoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOBnAL4AAAFX3C0NAAAAAElFTkSuQmCC', 'base64'),
     17999, -- $179.99
     53,
     1, -- AVAILABLE
     false),

-- Sports & Outdoors (Green #16A34A)
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
     'Metallic Knit Tank Top',
     'Fitted metallic knit tank top with subtle shimmer. Ribbed texture with a comfortable square neckline and wide shoulder straps. Versatile wardrobe staple that pairs with jeans, trousers, or skirts.',
     decode('iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAABmJLR0QA/wD/AP+gvaeTAAAAVklEQVR4nO3BMQEAAADCoPVPbQwfoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOBnABajAAEd9TKnAAAAAElFTkSuQmCC', 'base64'),
     3499, -- $34.99
     78,
     1, -- AVAILABLE
     false),

    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
     'Stainless Steel Water Bottle',
     'Insulated water bottle keeps drinks cold for 24 hours or hot for 12 hours. BPA-free with leak-proof design.',
     decode('iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAABmJLR0QA/wD/AP+gvaeTAAAAVklEQVR4nO3BMQEAAADCoPVPbQwfoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOBnABajAAEd9TKnAAAAAElFTkSuQmCC', 'base64'),
     2999, -- $29.99
     142,
     1, -- AVAILABLE
     false),

    ('cccccccc-cccc-cccc-cccc-cccccccccccc',
     'Perforated Slip-On Shoes',
     'Breathable perforated slip-on shoes in natural suede. Flexible sole with tassel accent. Easy on-off design with a comfortable fit for all-day wear.',
     decode('iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAABmJLR0QA/wD/AP+gvaeTAAAAVklEQVR4nO3BMQEAAADCoPVPbQwfoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOBnABajAAEd9TKnAAAAAElFTkSuQmCC', 'base64'),
     8999, -- $89.99
     64,
     1, -- AVAILABLE
     false),

-- Fashion & Accessories (Purple #9333EA)
    ('dddddddd-dddd-dddd-dddd-dddddddddddd',
     'Suede Tassel Loafers',
     'Classic suede loafers with decorative tassel detail and perforated upper. Lightweight construction with cushioned insole. Versatile slip-on style suitable for casual or smart-casual occasions.',
     decode('iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAABmJLR0QA/wD/AP+gvaeTAAAAVklEQVR4nO3BMQEAAADCoPVPbQwfoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOBnAJM+AAEOYaJkAAAAAElFTkSuQmCC', 'base64'),
     12999, -- $129.99
     37,
     1, -- AVAILABLE
     false),

    ('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
     'Sunglasses Polarized',
     'Classic polarized sunglasses with UV400 protection. Stylish design with durable frame and scratch-resistant lenses.',
     decode('iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAABmJLR0QA/wD/AP+gvaeTAAAAVklEQVR4nO3BMQEAAADCoPVPbQwfoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOBnAJM+AAEOYaJkAAAAAElFTkSuQmCC', 'base64'),
     5999, -- $59.99
     91,
     1, -- AVAILABLE
     false),

    ('ffffffff-ffff-ffff-ffff-ffffffffffff',
     'Minimalist Watch',
     'Elegant minimalist watch with genuine leather strap and stainless steel case. Water-resistant with Japanese quartz movement.',
     decode('iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAABmJLR0QA/wD/AP+gvaeTAAAAVklEQVR4nO3BMQEAAADCoPVPbQwfoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOBnAJM+AAEOYaJkAAAAAElFTkSuQmCC', 'base64'),
     9999, -- $99.99
     48,
     1, -- AVAILABLE
     false),

-- Kitchen & Dining (Red #DC2626)
    ('10101010-1010-1010-1010-101010101010',
     'Matte Black Coffee Mug',
     'Stylish matte black ceramic coffee mug with contrasting golden interior. 14oz capacity. Ergonomic handle design. Microwave and dishwasher safe.',
     decode('iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAABmJLR0QA/wD/AP+gvaeTAAAAVklEQVR4nO3BMQEAAADCoPVPbQwfoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOBnANwmAAHzl19QAAAAAElFTkSuQmCC', 'base64'),
     7999, -- $79.99
     56,
     1, -- AVAILABLE
     false),

    ('20202020-2020-2020-2020-202020202020',
     'Salt & Pepper Mill Set',
     'Elegant acrylic salt and pepper mill set with stainless steel tops. Twist-action grinders with adjustable coarseness settings. Clear body lets you see when refill is needed.',
     decode('iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAABmJLR0QA/wD/AP+gvaeTAAAAVklEQVR4nO3BMQEAAADCoPVPbQwfoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOBnANwmAAHzl19QAAAAAElFTkSuQmCC', 'base64'),
     14999, -- $149.99
     29,
     1, -- AVAILABLE
     false),

    ('30303030-3030-3030-3030-303030303030',
     'Acrylic Spice Grinder Duo',
     'Matching pair of acrylic spice grinders for salt and peppercorns. Classic design with premium grinding mechanism. Dishwasher-safe reservoir for easy cleaning.',
     decode('iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAABmJLR0QA/wD/AP+gvaeTAAAAVklEQVR4nO3BMQEAAADCoPVPbQwfoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOBnANwmAAHzl19QAAAAAElFTkSuQmCC', 'base64'),
     9999, -- $99.99
     42,
     1, -- AVAILABLE
     false),

-- Personal Care (Teal #0D9488)
    ('40404040-4040-4040-4040-404040404040',
     'Electric Toothbrush',
     'Rechargeable electric toothbrush with 5 cleaning modes and pressure sensor. Includes 4 brush heads and travel case.',
     decode('iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAABmJLR0QA/wD/AP+gvaeTAAAAVklEQVR4nO3BMQEAAADCoPVPbQwfoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOBnAA2UiADbZQolAAAAAElFTkSuQmCC', 'base64'),
     6999, -- $69.99
     73,
     1, -- AVAILABLE
     false),

    ('50505050-5050-5050-5050-505050505050',
     'Hair Dryer Professional',
     'Professional ionic hair dryer with 3 heat settings and 2 speed settings. Includes concentrator and diffuser attachments.',
     decode('iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAABmJLR0QA/wD/AP+gvaeTAAAAVklEQVR4nO3BMQEAAADCoPVPbQwfoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOBnAA2UiADbZQolAAAAAElFTkSuQmCC', 'base64'),
     5999, -- $59.99
     51,
     1, -- AVAILABLE
     false),

-- Gaming (Magenta #C026D3)
    ('60606060-6060-6060-6060-606060606060',
     'Gaming Mouse RGB',
     'High-precision gaming mouse with customizable RGB lighting and programmable buttons. Features adjustable DPI up to 16000.',
     decode('iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAABmJLR0QA/wD/AP+gvaeTAAAAVklEQVR4nO3BMQEAAADCoPVPbQwfoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOBnAMAm0wHJzPqQAAAAAElFTkSuQmCC', 'base64'),
     5999, -- $59.99
     84,
     1, -- AVAILABLE
     false),

    ('70707070-7070-7070-7070-707070707070',
     'Gaming Headset',
     'Immersive gaming headset with 7.1 surround sound and noise-canceling microphone. Comfortable memory foam ear cushions.',
     decode('iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAABmJLR0QA/wD/AP+gvaeTAAAAVklEQVR4nO3BMQEAAADCoPVPbQwfoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOBnAMAm0wHJzPqQAAAAAElFTkSuQmCC', 'base64'),
     8999, -- $89.99
     62,
     1, -- AVAILABLE
     false),

-- Limited Stock Items (Gold #CA8A04)
    ('80808080-8080-8080-8080-808080808080',
     'Vintage Record Player',
     'Retro-style record player with built-in speakers and Bluetooth connectivity. Plays 33, 45, and 78 RPM records.',
     decode('iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAABmJLR0QA/wD/AP+gvaeTAAAAVklEQVR4nO3BMQEAAADCoPVPbQwfoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOBnAMqKCAEn0PprAAAAAElFTkSuQmCC', 'base64'),
     19999, -- $199.99
     8,
     1, -- AVAILABLE
     false),

    ('90909090-9090-9090-9090-909090909090',
     'Premium Camera Tripod',
     'Professional carbon fiber tripod with ball head. Supports up to 30 lbs with adjustable height from 20 to 67 inches.',
     decode('iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAABmJLR0QA/wD/AP+gvaeTAAAAVklEQVR4nO3BMQEAAADCoPVPbQwfoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOBnAMqKCAEn0PprAAAAAElFTkSuQmCC', 'base64'),
     15999, -- $159.99
     12,
     1, -- AVAILABLE
     false),

-- High-End Items (Gold #CA8A04)
    ('a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1',
     'Two-Tone Ceramic Mug',
     'Modern two-tone ceramic mug with matte black exterior and warm yellow interior. 12oz capacity. Microwave and dishwasher safe. Perfect for coffee, tea, or any hot beverage.',
     decode('iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAABmJLR0QA/wD/AP+gvaeTAAAAVklEQVR4nO3BMQEAAADCoPVPbQwfoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOBnAMqKCAEn0PprAAAAAElFTkSuQmCC', 'base64'),
     49999, -- $499.99
     6,
     1, -- AVAILABLE
     false)
ON CONFLICT (id) DO NOTHING;

-- Add some off-shelf products for testing admin functionality (Gray #6B7280)
INSERT INTO products (id, name, description, image_data, price_per_unit, count_in_stock, state, is_deleted)
VALUES
    ('b1b1b1b1-b1b1-b1b1-b1b1-b1b1b1b1b1b1',
     'Tablet Computer (Previous Generation)',
     'Previous generation tablet computer. Currently off-shelf while new model is being prepared.',
     decode('iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAABmJLR0QA/wD/AP+gvaeTAAAAVklEQVR4nO3BMQEAAADCoPVPbQwfoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOBnAGtyiwCKs+DjAAAAAElFTkSuQmCC', 'base64'),
     39999, -- $399.99
     5,
     2, -- OFF_SHELF
     false)
ON CONFLICT (id) DO NOTHING;
