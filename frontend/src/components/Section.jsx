import React from 'react';
import { motion } from 'framer-motion';
import { useInView } from 'framer-motion';
import { useRef } from 'react';

const Section = ({ id, title, children, className = '', background = 'bg-gray-900' }) => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, threshold: 0.1 });

  return (
    <section id={id} className={`py-20 ${background} ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          ref={ref}
          initial={{ opacity: 0, y: 50 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 50 }}
          transition={{ duration: 0.8 }}
        >
          <h2 className="section-title section-divider text-3xl md:text-4xl font-bold text-white mb-12">
            {title}
          </h2>
          {children}
        </motion.div>
      </div>
    </section>
  );
};

export default Section;

