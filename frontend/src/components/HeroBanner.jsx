import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import banner1 from '../assets/banner1.png';
import banner2 from '../assets/banner2.png';
import banner3 from '../assets/banner3.png';
import banner4 from '../assets/banner4.png';

const HeroBanner = () => {
  const [currentBanner, setCurrentBanner] = useState(0);
  
  const banners = [
    { image: banner1, title: '鬼谷文化', subtitle: '纵横捭阖，古今通达' },
    { image: banner2, title: '法天象地', subtitle: '国学指引，人生赋能' },
    { image: banner3, title: '国学传承', subtitle: '强者风范，生生不息' },
    { image: banner4, title: '道家智慧', subtitle: '天人合一，道法自然' }
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentBanner((prev) => (prev + 1) % banners.length);
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  return (
    <section className="relative h-screen overflow-hidden">
      {/* Background Images */}
      {banners.map((banner, index) => (
        <motion.div
          key={index}
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url(${banner.image})` }}
          initial={{ opacity: 0 }}
          animate={{ opacity: index === currentBanner ? 1 : 0 }}
          transition={{ duration: 1.5 }}
        />
      ))}
      
      {/* Overlay */}
      <div className="absolute inset-0 bg-black/50" />
      
      {/* Content */}
      <div className="relative z-10 h-full flex items-center justify-center text-center">
        <motion.div
          key={currentBanner}
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
          className="max-w-4xl mx-auto px-4"
        >
          <h1 className="hero-title text-5xl md:text-7xl font-bold text-white mb-6">
            {banners[currentBanner].title}
          </h1>
          <p className="text-xl md:text-2xl text-gray-300 mb-8">
            {banners[currentBanner].subtitle}
          </p>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => document.getElementById('about').scrollIntoView({ behavior: 'smooth' })}
            className="bg-gray-800/80 hover:bg-gray-700/80 text-white px-8 py-3 rounded-lg text-lg font-medium transition-all duration-300 backdrop-blur-sm border border-gray-600"
          >
            探索智慧之门
          </motion.button>
        </motion.div>
      </div>
      
      {/* Banner Indicators */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 flex space-x-2">
        {banners.map((_, index) => (
          <button
            key={index}
            onClick={() => setCurrentBanner(index)}
            className={`w-3 h-3 rounded-full transition-all duration-300 ${
              index === currentBanner ? 'bg-white' : 'bg-white/50'
            }`}
          />
        ))}
      </div>
    </section>
  );
};

export default HeroBanner;

