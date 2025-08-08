import { Link, useLocation } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Home, User, LogOut, MessageCircle, Settings } from 'lucide-react'

const Sidebar = ({ user, onLogout }) => {
  const location = useLocation()

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: Home },
    { name: 'Profile', href: '/profile', icon: User },
    { name: 'AI Assistant', href: '/ai-assistant', icon: MessageCircle },
  ]

  if (user.is_admin) {
    navigation.push({ name: 'Admin Panel', href: '/admin', icon: Settings })
  }

  return (
    <div className="w-64 bg-white shadow-lg">
      <div className="p-6">
        <h1 className="text-2xl font-bold text-teal-600">ScholarSync</h1>
      </div>
      
      <nav className="mt-6">
        {navigation.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.href
          
          return (
            <Link
              key={item.name}
              to={item.href}
              className={`flex items-center px-6 py-3 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-teal-50 text-teal-700 border-r-2 border-teal-600'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <Icon className="mr-3 h-5 w-5" />
              {item.name}
            </Link>
          )
        })}
      </nav>

      <div className="absolute bottom-0 w-64 p-6">
        <div className="flex items-center mb-4">
          <div className="w-8 h-8 bg-teal-600 rounded-full flex items-center justify-center">
            <span className="text-white text-sm font-semibold">
              {user.full_name.charAt(0).toUpperCase()}
            </span>
          </div>
          <div className="ml-3">
            <p className="text-sm font-medium text-gray-900">{user.full_name}</p>
            <p className="text-xs text-gray-500">Student</p>
          </div>
        </div>
        <Button
          onClick={onLogout}
          variant="outline"
          size="sm"
          className="w-full"
        >
          <LogOut className="mr-2 h-4 w-4" />
          Logout
        </Button>
      </div>
    </div>
  )
}

export default Sidebar

