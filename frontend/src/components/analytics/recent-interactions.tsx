import { MessageSquare, Phone, Mail, Video, Calendar, User } from 'lucide-react'
import { formatDateTime } from '@/lib/utils'

const interactions = [
  {
    id: 1,
    type: 'email',
    description: 'Follow-up email sent to John Doe',
    entity: 'Acme Corp',
    user: 'Sarah Johnson',
    timestamp: '2024-01-15T10:30:00Z',
    icon: Mail,
    color: 'bg-blue-500',
  },
  {
    id: 2,
    type: 'call',
    description: 'Product demo call completed',
    entity: 'TechStart Inc',
    user: 'Mike Chen',
    timestamp: '2024-01-15T09:15:00Z',
    icon: Phone,
    color: 'bg-green-500',
  },
  {
    id: 3,
    type: 'meeting',
    description: 'Quarterly review meeting scheduled',
    entity: 'Global Solutions',
    user: 'Emily Davis',
    timestamp: '2024-01-15T08:45:00Z',
    icon: Calendar,
    color: 'bg-purple-500',
  },
  {
    id: 4,
    type: 'video',
    description: 'Video conference with potential client',
    entity: 'Innovation Labs',
    user: 'David Wilson',
    timestamp: '2024-01-14T16:20:00Z',
    icon: Video,
    color: 'bg-orange-500',
  },
  {
    id: 5,
    type: 'message',
    description: 'Chat support interaction resolved',
    entity: 'StartupXYZ',
    user: 'Lisa Anderson',
    timestamp: '2024-01-14T14:30:00Z',
    icon: MessageSquare,
    color: 'bg-pink-500',
  },
]

export function RecentInteractions() {
  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
          Recent Interactions
        </h3>
        <div className="flow-root">
          <ul className="-mb-8">
            {interactions.map((interaction, interactionIdx) => (
              <li key={interaction.id}>
                <div className="relative pb-8">
                  {interactionIdx !== interactions.length - 1 ? (
                    <span
                      className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                      aria-hidden="true"
                    />
                  ) : null}
                  <div className="relative flex space-x-3">
                    <div>
                      <span className={`h-8 w-8 rounded-full ${interaction.color} flex items-center justify-center ring-8 ring-white`}>
                        <interaction.icon className="h-4 w-4 text-white" />
                      </span>
                    </div>
                    <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                      <div>
                        <p className="text-sm text-gray-900">
                          {interaction.description}
                        </p>
                        <div className="mt-1 flex items-center space-x-2 text-sm text-gray-500">
                          <span className="flex items-center">
                            <User className="h-3 w-3 mr-1" />
                            {interaction.user}
                          </span>
                          <span>•</span>
                          <span>{interaction.entity}</span>
                        </div>
                      </div>
                      <div className="text-right text-sm whitespace-nowrap text-gray-500">
                        <time>{formatDateTime(interaction.timestamp)}</time>
                      </div>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}
