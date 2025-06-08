-- Drop the table if it exists
DROP TABLE IF EXISTS lectures;

-- Create the lectures table
CREATE TABLE lectures (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    course_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    thumbnail_url VARCHAR(255),
    lecture_url VARCHAR(255) NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add indexes
CREATE INDEX idx_lectures_course_id ON lectures(course_id);
CREATE INDEX idx_lectures_created_at ON lectures(created_at);
CREATE INDEX idx_lectures_is_active ON lectures(is_active);

-- Add sample data
INSERT INTO lectures (name, description, course_id, lecture_url, is_active) VALUES
('Introduction to Financial Astrology', 'Learn the basics of financial astrology and its applications in trading.', 1, 'https://example.com/videos/intro.mp4', TRUE),
('Planetary Cycles and Market Trends', 'Understanding how planetary cycles influence market movements.', 1, 'https://example.com/videos/cycles.mp4', TRUE); 