import React, { useEffect, useState } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';

const ScrollProgress = () => {
  const { scrollYProgress } = useScroll();
  
  return (
    <motion.div
      className="fixed top-0 left-0 right-0 h-1 bg-gradient-to-r from-gray-600 to-gray-400 z-50"
      style={{ scaleX: scrollYProgress, transformOrigin: '0%' }}
    />
  );
};

const ParallaxSection = ({ children, offset = 50 }) => {
  const { scrollY } = useScroll();
  const y = useTransform(scrollY, [0, 1000], [0, offset]);
  
  return (
    <motion.div style={{ y }}>
      {children}
    </motion.div>
  );
};

const FadeInWhenVisible = ({ children, delay = 0 }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, threshold: 0.1 }}
      transition={{ duration: 0.8, delay }}
    >
      {children}
    </motion.div>
  );
};

const FloatingElement = ({ children, duration = 6 }) => {
  return (
    <motion.div
      animate={{
        y: [-10, 10, -10],
      }}
      transition={{
        duration,
        repeat: Infinity,
        ease: "easeInOut"
      }}
    >
      {children}
    </motion.div>
  );
};

const StaggerContainer = ({ children, staggerDelay = 0.1 }) => {
  return (
    <motion.div
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, threshold: 0.1 }}
      variants={{
        hidden: {},
        visible: {
          transition: {
            staggerChildren: staggerDelay
          }
        }
      }}
    >
      {children}
    </motion.div>
  );
};

const StaggerItem = ({ children }) => {
  return (
    <motion.div
      variants={{
        hidden: { opacity: 0, y: 30 },
        visible: { opacity: 1, y: 0 }
      }}
      transition={{ duration: 0.6 }}
    >
      {children}
    </motion.div>
  );
};

export { 
  ScrollProgress, 
  ParallaxSection, 
  FadeInWhenVisible, 
  FloatingElement, 
  StaggerContainer, 
  StaggerItem 
};

