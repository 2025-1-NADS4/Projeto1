import React, { useState, useEffect, useRef } from 'react';
import { FaMapMarkerAlt } from 'react-icons/fa';

type estimativeResponse = {
  uberX: number;
  uberComfort: number;
  uberBlack: number;
};
declare global {
  interface Window {
    google: typeof google;
  }
}

const GOOGLE_API_KEY = '';

const UberFareEstimator: React.FC = () => {
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [estimative, setEstimative] = useState<estimativeResponse | null>(null);

  const originRef = useRef<HTMLInputElement | null>(null);
  const destinationRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    const loadGoogleMapsScript = () => {
      if (typeof window.google === 'undefined') {
        const script = document.createElement('script');
        script.src = `https://maps.googleapis.com/maps/api/js?key=${GOOGLE_API_KEY}&libraries=places`;
        script.async = true;
        script.onload = initAutocomplete;
        document.body.appendChild(script);
      } else {
        initAutocomplete();
      }
    };

    const initAutocomplete = () => {
      if (originRef.current) {
        const autocompleteOrigin = new window.google.maps.places.Autocomplete(originRef.current);
        autocompleteOrigin.addListener('place_changed', () => {
          const place = autocompleteOrigin.getPlace();
          setOrigin(place.formatted_address ?? '');
        });
      }

      if (destinationRef.current) {
        const autocompleteDest = new window.google.maps.places.Autocomplete(destinationRef.current);
        autocompleteDest.addListener('place_changed', () => {
          const place = autocompleteDest.getPlace();
          setDestination(place.formatted_address ?? '');
        });
      }
    };

    loadGoogleMapsScript();
  }, []);

  const handleEstimate = async () => {
    setLoading(true);
    setError(null);
    setEstimative(null);

    try {
      const response = await fetch('http://127.0.0.1:8000/estimative', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ origem: origin, destino: destination }),
      });

      if (!response.ok) throw new Error('Erro na requisição');

      const data: estimativeResponse = await response.json();
      setEstimative(data);
    } catch (error) {
      console.error('Erro ao buscar estimativa:', error);
      setError('Ocorreu um erro ao buscar a estimativa. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className='min-h-screen flex flex-col items-center justify-center p-4 bg-gray-50 text-gray-800'>
      <h1 className='text-2xl font-bold mb-4'>Estimativa de Corrida Uber</h1>

      <div className='flex flex-col gap-3 w-full max-w-md'>
        <div className='flex items-center gap-2 border border-gray-300 rounded px-3 py-2 bg-white'>
          <FaMapMarkerAlt className='text-gray-500' />
          <input
            type='text'
            placeholder='Origem'
            ref={originRef}
            className='flex-1 outline-none'
          />
        </div>

        <div className='flex items-center gap-2 border border-gray-300 rounded px-3 py-2 bg-white'>
          <FaMapMarkerAlt className='text-gray-500' />
          <input
            type='text'
            placeholder='Destino'
            ref={destinationRef}
            className='flex-1 outline-none'
          />
        </div>

        <button
          onClick={handleEstimate}
          disabled={loading}
          className='bg-[#609f13] text-white rounded p-2 hover:bg-[#4e850f] disabled:opacity-50'
        >
          {loading ? 'Calculando...' : 'Obter valores'}
        </button>
      </div>

      {error && <div className='mt-4 text-red-600'>{error}</div>}

      {estimative && (
        <div className='mt-6 w-full max-w-md bg-white p-4 rounded shadow'>
          <ul className='space-y-1 text-xl'>
            <li><strong>UberX:</strong> R$ {estimative.uberX}</li>
            <hr />
            <li><strong>Uber Comfort:</strong> R$ {estimative.uberComfort}</li>
            <hr />
            <li><strong>Uber Black:</strong> R$ {estimative.uberBlack}</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default UberFareEstimator;
