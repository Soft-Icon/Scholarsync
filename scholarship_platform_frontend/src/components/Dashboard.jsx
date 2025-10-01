import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { User, LogOut, Search, MessageCircle, Settings } from 'lucide-react'
import Sidebar from './Sidebar'
import { BASE_URL } from '@/lib/utils'

const Dashboard = ({ user, onLogout }) => {
  const [suggestedScholarships, setSuggestedScholarships] = useState([])
  const [applications, setApplications] = useState([])
  const [searchResults, setSearchResults] = useState([])
  const [showSearch, setShowSearch] = useState(false)
  const [searchFilters, setSearchFilters] = useState({
    country: '',
    level: '',
    field: '',
    deadline: ''
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchSuggestedScholarships()
    fetchApplications()
    // Trigger AI matching on component mount
    triggerAIMatching()
  }, [])

  const triggerAIMatching = async () => {
    try {
      const response = await fetch(`/api/ai/match-scholarships`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      })
      if (response.ok) {
        fetchSuggestedScholarships()
      } else {
        console.error('AI matching failed with status:', response.status)
      }
    } catch (error) {
      console.error('AI matching failed:', error)
    }
  }

  const fetchSuggestedScholarships = async () => {
    try {
      const response = await fetch(`/api/scholarships/suggested`, { credentials: 'include' })
      if (response.ok) {
        const data = await response.json()
        setSuggestedScholarships(data.suggested_scholarships || [])
      }
    } catch (error) {
      console.error('Failed to fetch suggested scholarships:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchApplications = async () => {
    try {
      const response = await fetch(`/api/applications/`, { credentials: 'include' })
      if (response.ok) {
        const data = await response.json()
        setApplications(data.applications || [])
      }
    } catch (error) {
      console.error('Failed to fetch applications:', error)
    }
  }

  const handleSearch = async () => {
    try {
      const params = new URLSearchParams()
      Object.entries(searchFilters).forEach(([key, value]) => {
        if (value) params.append(key, value)
      })

      const response = await fetch(`/api/scholarships/?${params}`, { credentials: 'include' })
      if (response.ok) {
        const data = await response.json()
        setSearchResults(data.scholarships || [])
        setShowSearch(true)
      }
    } catch (error) {
      console.error('Search failed:', error)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'Submitted': return 'bg-blue-100 text-blue-800'
      case 'Under Review': return 'bg-yellow-100 text-yellow-800'
      case 'Awaiting Result': return 'bg-purple-100 text-purple-800'
      case 'Draft': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getMatchColor = (percentage) => {
    if (percentage >= 80) return 'text-green-600'
    if (percentage >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-teal-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar user={user} onLogout={onLogout} />
      
      <div className="flex-1 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Welcome back, {user.full_name}!
            </h1>
            <p className="text-gray-600">
              Discover scholarships tailored for your profile
            </p>
          </div>

          {/* Search & Filter Section */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Search className="h-5 w-5" />
                Search & Filter
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                <Select onValueChange={(value) => setSearchFilters({...searchFilters, country_info: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select country" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="nigeria">Nigeria</SelectItem>
                    <SelectItem value="uk">UK</SelectItem>
                    <SelectItem value="usa">USA</SelectItem>
                    <SelectItem value="canada">Canada</SelectItem>
                  </SelectContent>
                </Select>

                <Select onValueChange={(value) => setSearchFilters({...searchFilters, level: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Level of study" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="undergraduate">Undergraduate</SelectItem>
                    <SelectItem value="masters">Masters</SelectItem>
                    <SelectItem value="phd">PhD</SelectItem>
                  </SelectContent>
                </Select>

                <Input
                  placeholder="Field of study"
                  value={searchFilters.field}
                  onChange={(e) => setSearchFilters({...searchFilters, field: e.target.value})}
                />

                <Input
                  placeholder="Deadline (e.g., Before 31 Jul)"
                  value={searchFilters.deadline}
                  onChange={(e) => setSearchFilters({...searchFilters, deadline: e.target.value})}
                />
              </div>
              <Button onClick={handleSearch} className="bg-teal-600 hover:bg-teal-700">
                Search
              </Button>
            </CardContent>
          </Card>

          {/* Search Results */}
          {showSearch && (
            <Card className="mb-8">
              <CardHeader>
                <CardTitle>Search Results</CardTitle>
                <CardDescription>
                  Found {searchResults.length} scholarships matching your criteria
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {searchResults.map((scholarship) => (
                    <Card key={scholarship.id} className="hover:shadow-lg transition-shadow">
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <Badge variant="outline">{scholarship.country_info}</Badge>
                        </div>
                        <CardTitle className="text-lg">{scholarship.title}</CardTitle>
                        <CardDescription>
                          {scholarship.level_of_study} • {scholarship.field_of_study}
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-gray-600 mb-2">
                          Deadline: {scholarship.deadline}
                        </p>
                        <div className="flex gap-2">
                          <Button size="sm" className="bg-teal-600 hover:bg-teal-700">
                            Apply
                          </Button>
                          <Button size="sm" variant="outline">
                            Details
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Suggested Scholarships */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Suggested Scholarships</CardTitle>
              <CardDescription>
                Based on your profile, here are scholarships that match your background
              </CardDescription>
            </CardHeader>
            <CardContent>
              {suggestedScholarships.length === 0 ? (
                <p className="text-gray-500 text-center py-8">
                  No suggested scholarships yet. Complete your profile to get personalized recommendations.
                </p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {suggestedScholarships.map((scholarship) => (
                    <Card key={scholarship.id} className="hover:shadow-lg transition-shadow">
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <Badge variant="outline">{scholarship.country_info}</Badge>
                          <span className={`text-sm font-semibold ${getMatchColor(scholarship.match_percentage)}`}>
                            Match: {scholarship.match_percentage}%
                          </span>
                        </div>
                        <CardTitle className="text-lg">{scholarship.title}</CardTitle>
                        <CardDescription>
                          {scholarship.level_of_study} • {scholarship.field_of_study}
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-gray-600 mb-2">
                          Deadline: {scholarship.deadline}
                        </p>
                        <div className="flex gap-2">
                          <Button size="sm" className="bg-teal-600 hover:bg-teal-700">
                            Apply
                          </Button>
                          <Button size="sm" variant="outline">
                            Details
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Application Status */}
          <Card>
            <CardHeader>
              <CardTitle>Application Status</CardTitle>
              <CardDescription>
                Track your scholarship applications
              </CardDescription>
            </CardHeader>
            <CardContent>
              {applications.length === 0 ? (
                <p className="text-gray-500 text-center py-8">
                  No applications yet. Start applying to scholarships to track your progress here.
                </p>
              ) : (
                <div className="space-y-4">
                  {applications.map((application) => (
                    <div key={application.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div>
                        <h3 className="font-semibold">{application.scholarship_title}</h3>
                        <p className="text-sm text-gray-600">
                          Applied: {application.applied_date ? new Date(application.applied_date).toLocaleDateString() : 'Not submitted'}
                        </p>
                      </div>
                      <div className="flex items-center gap-4">
                        <Badge className={getStatusColor(application.status)}>
                          {application.status}
                        </Badge>
                        {application.match_percentage && (
                          <span className={`text-sm font-semibold ${getMatchColor(application.match_percentage)}`}>
                            {application.match_percentage}%
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default Dashboard

